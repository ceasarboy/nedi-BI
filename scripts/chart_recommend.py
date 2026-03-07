import json
import sys
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

def detect_data_type(column_name: str, value: Any) -> str:
    if value is None:
        return "unknown"

    value_str = str(value)

    if isinstance(value, (int, float)):
        return "numeric"

    column_lower = column_name.lower()

    date_keywords = ['date', 'time', 'year', 'month', 'day', 'datetime', 'timestamp', 'created', 'updated']
    if any(kw in column_lower for kw in date_keywords):
        return "date"

    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}',
        r'^\d{4}/\d{2}/\d{2}',
        r'^\d{2}-\d{2}-\d{4}',
        r'^\d{4}\d{2}\d{2}$',
    ]
    for pattern in date_patterns:
        if re.match(pattern, value_str):
            return "date"

    if '年' in value_str or '月' in value_str or '日' in value_str:
        return "date"

    return "string"

def analyze_columns(data: List[Dict]) -> Dict[str, Any]:
    if not data:
        return {"columns": [], "primary_key": None}

    first_row = data[0]
    columns = []

    for col_name, value in first_row.items():
        col_type = detect_data_type(col_name, value)
        columns.append({
            "name": col_name,
            "type": col_type,
            "sample_values": list(set([str(row.get(col_name)) for row in data[:3] if row.get(col_name) is not None]))[:3]
        })

    numeric_cols = [c for c in columns if c["type"] == "numeric"]
    date_cols = [c for c in columns if c["type"] == "date"]
    string_cols = [c for c in columns if c["type"] == "string"]

    return {
        "columns": columns,
        "numeric_columns": numeric_cols,
        "date_columns": date_cols,
        "string_columns": string_cols,
        "total_rows": len(data),
        "total_columns": len(columns)
    }

def detect_chart_type(data: List[Dict], sql: str = "", history: str = "") -> Dict[str, Any]:
    if not data:
        return {
            "chart_type": "table",
            "reason": "无数据"
        }

    analysis = analyze_columns(data)

    if analysis["total_rows"] == 1 and analysis["total_columns"] == 1:
        return {
            "chart_type": "kpi",
            "summary": f"关键指标值: {list(data[0].values())[0]}",
            "axis_mapping": {},
            "chart_config": {
                "title": "关键指标"
            }
        }

    if analysis["total_rows"] <= 10 and analysis["total_columns"] <= 3:
        all_numeric = len(analysis["numeric_columns"]) > 0
        all_categorical = len(analysis["string_columns"]) >= 1 and len(analysis["numeric_columns"]) == 1

        if all_categorical:
            category_col = analysis["string_columns"][0]
            value_col = analysis["numeric_columns"][0]

            total_value = sum(float(row.get(value_col["name"], 0)) for row in data if row.get(value_col["name"]) is not None)
            is_percentage = all(
                0 <= float(row.get(value_col["name"], 0)) <= 100
                for row in data
                if row.get(value_col["name"]) is not None
            )

            if is_percentage or (total_value > 0 and total_value <= 100):
                return {
                    "chart_type": "pie",
                    "summary": f"{category_col['name']}分布占比",
                    "axis_mapping": {
                        "category": category_col["name"],
                        "value": value_col["name"]
                    },
                    "chart_config": {
                        "title": f"{category_col['name']}占比分布",
                        "legend_position": "right"
                    }
                }

            return {
                "chart_type": "bar",
                "summary": f"{category_col['name']}对比",
                "axis_mapping": {
                    "x": category_col["name"],
                    "y": value_col["name"]
                },
                "chart_config": {
                    "title": f"{category_col['name']}对比",
                    "x_axis_label": category_col["name"],
                    "y_axis_label": value_col["name"]
                }
            }

    if len(analysis["date_columns"]) >= 1 and len(analysis["numeric_columns"]) >= 1:
        date_col = analysis["date_columns"][0]
        value_col = analysis["numeric_columns"][0]

        return {
            "chart_type": "line",
            "summary": f"{value_col['name']}趋势",
            "axis_mapping": {
                "x": date_col["name"],
                "y": value_col["name"]
            },
            "chart_config": {
                "title": f"{value_col['name']}趋势图",
                "x_axis_label": date_col["name"],
                "y_axis_label": value_col["name"]
            }
        }

    if len(analysis["numeric_columns"]) >= 2:
        return {
            "chart_type": "scatter",
            "summary": "相关性分析",
            "axis_mapping": {
                "x": analysis["numeric_columns"][0]["name"],
                "y": analysis["numeric_columns"][1]["name"]
            },
            "chart_config": {
                "title": f"{analysis['numeric_columns'][0]['name']} vs {analysis['numeric_columns'][1]['name']}"
            }
        }

    return {
        "chart_type": "table",
        "summary": "数据明细列表",
        "axis_mapping": {
            "columns": [c["name"] for c in analysis["columns"]]
        },
        "chart_config": {
            "title": "数据明细",
            "columns": [{"key": c["name"], "label": c["name"]} for c in analysis["columns"]]
        }
    }

def generate_summary(data: List[Dict], chart_type: str, analysis: Dict) -> str:
    if not data:
        return "无数据"

    if chart_type == "kpi":
        value = list(data[0].values())[0]
        return f"关键指标值: {value}"

    if chart_type == "line" and analysis["date_columns"]:
        date_col = analysis["date_columns"][0]
        value_col = analysis["numeric_columns"][0]
        values = [float(row.get(value_col["name"], 0)) for row in data if row.get(value_col["name"]) is not None]

        if len(values) >= 2:
            change = values[-1] - values[0]
            pct_change = (change / values[0] * 100) if values[0] != 0 else 0
            trend = "增长" if change > 0 else "下降"

            return f"数据从{values[0]:.2f}到{values[-1]:.2f}，{trend}了{abs(pct_change):.1f}%"

        return f"共{len(data)}个时间点的数据"

    if chart_type == "bar" and analysis["string_columns"]:
        category_col = analysis["string_columns"][0]
        value_col = analysis["numeric_columns"][0]

        values = [(row.get(category_col["name"]), float(row.get(value_col["name"], 0))) for row in data if row.get(value_col["name"]) is not None]

        if values:
            max_item = max(values, key=lambda x: x[1])
            return f"{category_col['name']}中{max_item[0]}最高，数值为{max_item[1]}"

    if chart_type == "pie" and analysis["string_columns"]:
        category_col = analysis["string_columns"][0]
        value_col = analysis["numeric_columns"][0]

        values = [(row.get(category_col["name"]), float(row.get(value_col["name"], 0))) for row in data if row.get(value_col["name"]) is not None]

        if values:
            total = sum(v[1] for v in values)
            max_item = max(values, key=lambda x: x[1])
            pct = max_item[1] / total * 100 if total > 0 else 0
            return f"{max_item[0]}占比最高，达到{pct:.1f}%"

    return f"共{len(data)}条数据，{analysis['total_columns']}个字段"

def generate_next_questions(chart_type: str, analysis: Dict, history: str) -> List[str]:
    questions = []

    if chart_type == "line":
        questions = [
            "为什么近期趋势发生变化？",
            "查看去年同期对比",
            "按月份环比分析"
        ]

    elif chart_type == "bar":
        if analysis["string_columns"]:
            col_name = analysis["string_columns"][0]["name"]
            questions = [
                f"为什么{col_name}表现最好？",
                f"查看{col_name}的明细数据",
                "按其他维度对比"
            ]

    elif chart_type == "pie":
        questions = [
            "占比变化的原因是什么？",
            "查看各分类的详细数据",
            "历史占比变化趋势"
        ]

    elif chart_type == "kpi":
        questions = [
            "这个指标的行业平均水平是多少？",
            "查看指标的详细构成",
            "按时间段分析指标变化"
        ]

    else:
        questions = [
            "查看更多明细数据",
            "按某个字段排序",
            "筛选特定条件的数据"
        ]

    return questions

def recommend_chart(data: List[Dict], sql: str = "", history: str = "") -> Dict[str, Any]:
    analysis = analyze_columns(data)
    chart_info = detect_chart_type(data, sql, history)
    chart_type = chart_info["chart_type"]

    summary = generate_summary(data, chart_type, analysis)
    next_questions = generate_next_questions(chart_type, analysis, history)

    data_insights = []

    if chart_type == "line" and analysis["numeric_columns"]:
        value_col = analysis["numeric_columns"][0]["name"]
        values = [float(row.get(value_col, 0)) for row in data if row.get(value_col) is not None]
        if values:
            data_insights.append(f"数值范围: {min(values):.2f} ~ {max(values):.2f}")
            data_insights.append(f"平均值: {sum(values)/len(values):.2f}")

    elif chart_type == "bar" and analysis["numeric_columns"]:
        value_col = analysis["numeric_columns"][0]["name"]
        values = [float(row.get(value_col, 0)) for row in data if row.get(value_col) is not None]
        if values:
            data_insights.append(f"总计: {sum(values):.2f}")
            data_insights.append(f"平均值: {sum(values)/len(values):.2f}")

    return {
        "summary": summary,
        "chart_type": chart_type,
        "axis_mapping": chart_info.get("axis_mapping", {}),
        "chart_config": chart_info.get("chart_config", {}),
        "data_insights": data_insights,
        "next_questions": next_questions
    }

def main():
    import argparse

    parser = argparse.ArgumentParser(description="图表推荐工具")
    parser.add_argument("--data", "-d", type=str, help="JSON格式的查询结果数据")
    parser.add_argument("--sql", "-s", type=str, default="", help="执行的SQL语句")
    parser.add_argument("--history", type=str, default="", help="用户历史提问")
    parser.add_argument("--file", "-f", type=str, help="包含JSON数据的文件路径")

    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif args.data:
        data = json.loads(args.data)
    else:
        print("请提供 --data 或 --file 参数")
        sys.exit(1)

    result = recommend_chart(data, args.sql, args.history)

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
