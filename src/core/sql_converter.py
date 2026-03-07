import sqlglot
from sqlglot import transpile
from typing import Dict, List, Tuple
import re

class PostgreSQLToSQLiteConverter:
    def __init__(self):
        self.unsupported_features = []
        self.conversion_count = 0

    def convert(self, sql: str) -> Tuple[str, List[str]]:
        warnings = []

        converted = sql

        converted = self._convert_interval(converted, warnings)
        converted = self._convert_now(converted, warnings)
        converted = self._convert_current_timestamp(converted, warnings)
        converted = self._convert_date_trunc(converted, warnings)
        converted = self._convert_extract(converted, warnings)
        converted = self._convert_concat(converted, warnings)
        converted = self._convert_string_agg(converted, warnings)
        converted = self._convert_array(converted, warnings)
        converted = self._convert_generate_series(converted, warnings)
        converted = self._convert_json(converted, warnings)
        converted = self._convert_bool_and_or(converted, warnings)
        converted = self._convert_distinct_on(converted, warnings)
        converted = self._convert_returning(converted, warnings)
        converted = self._convert_ilike(converted, warnings)
        converted = self._convert_true_false(converted, warnings)
        converted = self._convert_cast(converted, warnings)
        converted = self._convert_regex(converted, warnings)
        converted = self._convert_window_functions(converted, warnings)
        converted = self._convert_limit_offset(converted, warnings)

        try:
            result = transpile(converted, read="postgres", write="sqlite", identify=False)
            return result[0], warnings
        except Exception as e:
            warnings.append(f"SQLGlot转换错误: {str(e)}, 尝试直接转换")
            return converted, warnings

    def _convert_interval(self, sql: str, warnings: List[str]) -> str:
        pattern = r"INTERVAL\s+'([^']+)'"
        matches = re.findall(pattern, sql, re.IGNORECASE)
        for match in matches:
            warnings.append(f"INTERVAL '{match}' 已被移除，SQLite不直接支持INTERVAL")
        result = re.sub(pattern, "'0'", sql, flags=re.IGNORECASE)
        return result

    def _convert_now(self, sql: str, warnings: List[str]) -> str:
        result = sql
        if 'NOW()' in sql.upper():
            warnings.append("NOW() 已转换为 datetime('now')")
            result = re.sub(r'\bNOW\(\)', "datetime('now')", result, flags=re.IGNORECASE)
        return result

    def _convert_current_timestamp(self, sql: str, warnings: List[str]) -> str:
        result = sql
        if 'CURRENT_TIMESTAMP' in sql.upper():
            warnings.append("CURRENT_TIMESTAMP 已转换为 datetime('now')")
            result = re.sub(r'\bCURRENT_TIMESTAMP\b', "datetime('now')", result, flags=re.IGNORECASE)
        return result

    def _convert_date_trunc(self, sql: str, warnings: List[str]) -> str:
        pattern = r"DATE_TRUNC\('([^']+)',\s*([^)]+)\)"
        matches = re.findall(pattern, sql, re.IGNORECASE)
        for unit, field in matches:
            unit = unit.lower()
            if unit == 'year':
                replacement = f"strftime('%Y', {field})"
            elif unit == 'month':
                replacement = f"strftime('%Y-%m', {field})"
            elif unit == 'day':
                replacement = f"strftime('%Y-%m-%d', {field})"
            else:
                replacement = f"strftime('%Y-%m-%d %H:%M:%S', {field})"
                warnings.append(f"DATE_TRUNC('{unit}', ...) 已转换为 strftime")
            sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
        return sql

    def _convert_extract(self, sql: str, warnings: List[str]) -> str:
        pattern = r"EXTRACT\(([^)]+)\s+FROM\s+([^)]+)\)"
        matches = re.findall(pattern, sql, re.IGNORECASE)
        for field, source in matches:
            field = field.lower().strip()
            if field == 'year':
                replacement = f"strftime('%Y', {source})"
            elif field == 'month':
                replacement = f"strftime('%m', {source})"
            elif field == 'day':
                replacement = f"strftime('%d', {source})"
            elif field == 'hour':
                replacement = f"strftime('%H', {source})"
            elif field == 'minute':
                replacement = f"strftime('%M', {source})"
            elif field == 'second':
                replacement = f"strftime('%S', {source})"
            elif field == 'dow':
                replacement = f"(strftime('%w', {source}) + 1)"
            else:
                replacement = f"strftime('%Y-%m-%d %H:%M:%S', {source})"
                warnings.append(f"EXTRACT({field} FROM ...) 已转换为 strftime")
            sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
        return sql

    def _convert_concat(self, sql: str, warnings: List[str]) -> str:
        if 'CONCAT_WS' in sql.upper():
            warnings.append("CONCAT_WS 已转换为 SQLite 的 || 运算符")
            pattern = r"CONCAT_WS\('([^']+)',\s*([^)]+)\)"
            sql = re.sub(pattern, r"REPLACE(\2, '\1', ' ')", sql, flags=re.IGNORECASE)
        return sql

    def _convert_string_agg(self, sql: str, warnings: List[str]) -> str:
        if 'STRING_AGG' in sql.upper():
            warnings.append("STRING_AGG 已转换为 GROUP_CONCAT")
            sql = sql.replace('STRING_AGG', 'GROUP_CONCAT')
            sql = sql.replace('string_agg', 'group_concat')
            sql = sql.replace('String_Agg', 'Group_Concat')
        return sql

    def _convert_array(self, sql: str, warnings: List[str]) -> str:
        if 'ARRAY[' in sql.upper():
            warnings.append("ARRAY[...] 已转换为 JSON 数组")
            sql = sql.replace('ARRAY[', '[')
            sql = sql.replace('array[', '[')
            sql = sql.replace('Array[', '[')
        return sql

    def _convert_generate_series(self, sql: str, warnings: List[str]) -> str:
        if 'GENERATE_SERIES' in sql.upper():
            warnings.append("GENERATE_SERIES 不被SQLite支持，建议在应用层生成")
            sql = re.sub(r"GENERATE_SERIES\(([^,]+),\s*([^,]+),\s*([^)]+)\)", "1", sql, flags=re.IGNORECASE)
        return sql

    def _convert_json(self, sql: str, warnings: List[str]) -> str:
        if '->>' in sql:
            warnings.append("JSON 运算符 ->> 已转换为 json_extract")
            sql = sql.replace('->>', '->')
        if 'JSONB' in sql.upper():
            warnings.append("JSONB 已转换为 JSON")
            sql = sql.replace('JSONB', 'JSON')
            sql = sql.replace('jsonb', 'json')
        return sql

    def _convert_bool_and_or(self, sql: str, warnings: List[str]) -> str:
        if 'BOOL_AND' in sql.upper() or 'BOOL_OR' in sql.upper():
            warnings.append("BOOL_AND/BOOL_OR 已转换为 MAX/MIN")
            sql = sql.replace('BOOL_AND', 'MAX')
            sql = sql.replace('bool_and', 'max')
            sql = sql.replace('BOOL_OR', 'MIN')
            sql = sql.replace('bool_or', 'min')
        return sql

    def _convert_distinct_on(self, sql: str, warnings: List[str]) -> str:
        if 'DISTINCT ON' in sql.upper():
            warnings.append("DISTINCT ON 不被SQLite支持，已移除")
            sql = re.sub(r'DISTINCT ON\s*\([^)]+\)', 'DISTINCT', sql, flags=re.IGNORECASE)
        return sql

    def _convert_returning(self, sql: str, warnings: List[str]) -> str:
        if 'RETURNING' in sql.upper():
            warnings.append("RETURNING 不被SQLite支持，需要拆分语句")
            sql = re.sub(r'\s+RETURNING\s+.*', '', sql, flags=re.IGNORECASE)
        return sql

    def _convert_ilike(self, sql: str, warnings: List[str]) -> str:
        if 'ILIKE' in sql.upper():
            warnings.append("ILIKE 已转换为 LIKE (SQLite不区分大小写)")
            sql = sql.replace('ILIKE', 'LIKE')
            sql = sql.replace('ilike', 'like')
        return sql

    def _convert_true_false(self, sql: str, warnings: List[str]) -> str:
        result = sql
        if "= TRUE" in sql.upper():
            warnings.append("= TRUE 已转换为 = 1")
            result = re.sub(r'=\s*TRUE\b', '= 1', result, flags=re.IGNORECASE)
        if "= FALSE" in sql.upper():
            warnings.append("= FALSE 已转换为 = 0")
            result = re.sub(r'=\s*FALSE\b', '= 0', result, flags=re.IGNORECASE)
        return result

    def _convert_cast(self, sql: str, warnings: List[str]) -> str:
        if '::' in sql:
            warnings.append(":: 类型转换已移除")
            sql = re.sub(r'::INT\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::INTEGER\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::TEXT\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::VARCHAR\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::NUMERIC\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::DECIMAL\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::FLOAT\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::DOUBLE\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::BOOLEAN\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::DATE\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::TIMESTAMP\b', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'::\w+', '', sql)
        return sql

    def _convert_regex(self, sql: str, warnings: List[str]) -> str:
        if '~' in sql or '!~' in sql or '~*' in sql:
            warnings.append("正则表达式运算符已转换为 GLOB/REGEXP")
            sql = sql.replace('~*', 'GLOB')
            sql = sql.replace('!~', 'NOT GLOB')
            sql = sql.replace('~', 'GLOB')
        return sql

    def _convert_window_functions(self, sql: str, warnings: List[str]) -> str:
        if 'OVER' in sql.upper() and 'PARTITION BY' in sql.upper():
            warnings.append("窗口函数已标记，需要SQLite 3.25.0+支持")
        if 'RANK()' in sql.upper() or 'DENSE_RANK()' in sql.upper() or 'ROW_NUMBER()' in sql.upper():
            warnings.append("窗口函数已标记")
        return sql

    def _convert_limit_offset(self, sql: str, warnings: List[str]) -> str:
        if 'LIMIT' in sql.upper() and 'OFFSET' in sql.upper():
            warnings.append("LIMIT OFFSET 语法已保留")
        return sql


converter = PostgreSQLToSQLiteConverter()

def convert_postgres_to_sqlite(sql: str) -> Tuple[str, List[str]]:
    return converter.convert(sql)
