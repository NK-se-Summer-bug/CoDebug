import json
import openai
from pyarrow import nulls
from tenacity import retry, stop_after_attempt, wait_random_exponential

# def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=messages,
#         temperature=temperature,
#     )
#     return response.choices[0].message["content"]

def get_completion_from_messages(messages, model="deepseek-chat", temperature=0.0):
    client = openai.OpenAI(api_key='your_api_key',
                           base_url="https://api.deepseek.com")

    @retry(wait=wait_random_exponential(min=1, max=2), stop=stop_after_attempt(6))
    def completion_with_backoff(messages, model, temperature):
        return client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            # response_format={"type": "json_object"} # 可选，根据需求决定
        )

    completion = completion_with_backoff(messages=messages, model=model, temperature=temperature)
    response = completion.choices[0].message.content
    print(response)
    return response

def extract_triplets(document):
    """
    调用AI模型对单个文档进行关系三元组抽取，返回三元组列表。
    """
    prompt_for_rte = f"""请对以下文档进行关系三元组抽取。根据文档的具体内容，提取实际存在的实体和它们之间的关系。

文档内容：
{document}

要求：
1. 提取文档中真实出现的实体（人物、概念、技术、组织等）
2. 识别这些实体之间的真实关系
3. 每个三元组格式：(头实体, 尾实体, 关系类型)
4. 关系类型要具体描述实体间的联系
5. 至少提取3-8个不同的三元组
6. 确保三元组反映文档的主要内容

示例格式：
1.(Vue.js, JavaScript框架, 是一种)
2.(组件, Vue应用, 构成)
3.(数据绑定, 视图更新, 实现)

请根据上述文档内容提取三元组："""

    messages = [
        {'role': 'system', 'content': '你是一个专业的信息抽取助手，擅长从文本中提取实体关系。请仔细分析文档内容，提取准确、多样化的关系三元组。'},
        {'role': 'user', 'content': prompt_for_rte}
    ]
    
    # 只保留一次提问，temperature=0保证稳定性
    for _ in range(3):
        try:
            response = get_completion_from_messages(messages, temperature=0.3)  # 增加一点随机性
            return response
        except Exception as e:
            print("OpenAI API error:", e)
            print("Retrying in 2 seconds...")
            import time
            time.sleep(2)
    print("Failed to get completion from OpenAI API.")
    return ""

def parse_triplets(ai_response):
    """
    解析AI返回的文本，提取三元组列表。
    只保留 {"h": ..., "t": ..., "r": ...}，h/t/r 都为自然语言。
    适应如下格式：
    1. (queen, Snow-white, parent-child)
    2. (king, queen, spouse)
    ...
    """
    import re
    triplets = []
    lines = ai_response.strip().split('\n')
    for line in lines:
        # 去掉编号前缀和多余空格
        line = line.strip()
        # 允许处理"1. (...)"或"(...)"等格式
        line = re.sub(r'^\d+\.\s*', '', line)
        match = re.match(r"[\(\（]([^\(\),，]+)[,，]\s*([^\(\),，]+)[,，]\s*([^\(\),，]+)[\)\）]", line)
        if match:
            h, t, r = match.group(1).strip(), match.group(2).strip(), match.group(3).strip()
            triplets.append({"h": h, "t": t, "r": r})
    return triplets

def rte_from_text(document, output_path=None):
    """
    对输入文档逐条抽取三元组，保存到 output_path
    """
    results = []

    ai_response = extract_triplets(document)
    triplets = parse_triplets(ai_response)
    print("Extracted triplets:", triplets)
    for triplet in triplets:
        results.append(triplet)
    # 保存结果
    if output_path != None:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(results)} triplets to {output_path}")
    return results 