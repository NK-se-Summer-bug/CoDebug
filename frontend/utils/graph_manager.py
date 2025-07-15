# -*- coding: utf-8 -*-
"""
知识图谱管理模块
包含知识图谱的可视化、颜色生成、模板加载等功能
"""

import random
import re
from typing import Dict, List
from config.constants import GRAPH_TEMPLATE_PATHS


class GraphManager:
    """知识图谱管理器"""
    
    @staticmethod
    def get_random_color() -> str:
        """生成随机颜色"""
        r = random.randint(100, 200)
        g = random.randint(100, 200)
        b = random.randint(100, 200)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def generate_dynamic_graph_html(triplets: List[Dict]) -> str:
        """根据三元组动态生成graph.html内容"""
        if not triplets:
            return "<h3>当前还没有可显示的知识三元组。</h3>"
        
        # 为实体类型分配固定颜色
        entity_colors = {}
        
        nodes_set = set()
        nodes_js = []
        edges_js = []
        
        # 首先收集所有唯一的实体
        for triplet in triplets:
            h, r, t = triplet.get('h'), triplet.get('r'), triplet.get('t')
            if not all([h, r, t]):
                continue
                
            nodes_set.add(h)
            nodes_set.add(t)
        
        # 为每个实体分配颜色
        for entity in nodes_set:
            if entity not in entity_colors:
                entity_colors[entity] = GraphManager.get_random_color()
        
        # 生成节点数据
        for entity in nodes_set:
            color = entity_colors.get(entity, "#7DCEA0")
            border_color = color
            
            node_id = f'"{entity}"'
            nodes_js.append(f'{{id: {node_id}, label: "{entity}", title: "{entity}", ' +
                          f'color: {{ background: "{color}", border: "{border_color}" }}}}')
        
        # 生成边数据
        for triplet in triplets:
            h, r, t = triplet.get('h'), triplet.get('r'), triplet.get('t')
            if not all([h, r, t]):
                continue
                
            from_id = f'"{h}"'
            to_id = f'"{t}"'
            
            edges_js.append(f'{{from: {from_id}, to: {to_id}, arrows: "to", label: "{r}"}}')
        
        nodes_str = ",\n        ".join(nodes_js)
        edges_str = ",\n        ".join(edges_js)
        
        return GraphManager._load_graph_template(nodes_str, edges_str)
    
    @staticmethod
    def _load_graph_template(nodes_str: str, edges_str: str) -> str:
        """加载图谱模板并替换数据"""
        try:
            template_content = None
            used_path = None
            
            for path in GRAPH_TEMPLATE_PATHS:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                        used_path = path
                        break
                except FileNotFoundError:
                    continue
            
            if not template_content:
                raise FileNotFoundError("无法找到任何可用的图谱模板文件")
            
            # 替换占位符
            if "{{NODES_PLACEHOLDER}}" in template_content and "{{EDGES_PLACEHOLDER}}" in template_content:
                html_content = template_content.replace("{{NODES_PLACEHOLDER}}", nodes_str)
                html_content = html_content.replace("{{EDGES_PLACEHOLDER}}", edges_str)
            else:
                # 备用方案：使用正则表达式替换
                html_content = template_content
                
                # 替换节点数据
                nodes_pattern = r"var\s+nodes\s*=\s*new\s+vis\.DataSet\(\s*\[\s*"
                if re.search(nodes_pattern, html_content):
                    html_content = re.sub(
                        nodes_pattern + r".*?\]\s*\);",
                        f"var nodes = new vis.DataSet([{nodes_str}]);",
                        html_content,
                        flags=re.DOTALL
                    )
                
                # 替换边数据
                edges_pattern = r"var\s+edges\s*=\s*new\s+vis\.DataSet\(\s*\[\s*"
                if re.search(edges_pattern, html_content):
                    html_content = re.sub(
                        edges_pattern + r".*?\]\s*\);",
                        f"var edges = new vis.DataSet([{edges_str}]);",
                        html_content,
                        flags=re.DOTALL
                    )
            
            return html_content
            
        except FileNotFoundError as e:
            return f"<h3>错误：找不到图谱模板文件。</h3><p>尝试过的路径: {', '.join(GRAPH_TEMPLATE_PATHS)}</p>"
        except Exception as e:
            return f"<h3>生成图谱时出错: {e}</h3>"


# 为了保持向后兼容性，保留原来的类名
class GraphUtils(GraphManager):
    """图谱工具类（保持向后兼容性）"""
    pass
