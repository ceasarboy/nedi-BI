"""
三层记忆系统服务层
实现用户偏好、成功案例、失败教训的存储和检索
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
import json
import re

from src.core.database import SessionLocal
from src.models.memory import UserPreference, SuccessCase, FailureLesson


class MemoryService:
    """三层记忆系统服务"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def close(self):
        if self.db:
            self.db.close()
    
    # ==================== 用户偏好层 ====================
    
    def save_user_preference(
        self,
        user_id: Optional[int],
        preference_type: str,
        preference_key: str,
        preference_value: str,
        source: str = "auto"
    ) -> UserPreference:
        """保存用户偏好"""
        existing = self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.preference_key == preference_key
            )
        ).first()
        
        if existing:
            existing.preference_value = preference_value
            existing.confidence = min(existing.confidence + 0.1, 1.0)
            existing.updated_at = datetime.utcnow()
        else:
            existing = UserPreference(
                user_id=user_id,
                preference_type=preference_type,
                preference_key=preference_key,
                preference_value=preference_value,
                source=source,
                confidence=0.5
            )
            self.db.add(existing)
        
        self.db.commit()
        return existing
    
    def get_user_preferences(self, user_id: Optional[int], limit: int = 10) -> List[UserPreference]:
        """获取用户偏好"""
        return self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.active == True
        ).order_by(
            desc(UserPreference.confidence)
        ).limit(limit).all()
    
    def extract_preferences_from_positive_feedback(
        self,
        user_id: Optional[int],
        query: str,
        response: str
    ) -> List[str]:
        """从正面反馈中提取用户偏好"""
        preferences = []
        
        response_length = len(response)
        if response_length < 200:
            preferences.append(("style", "response_length", "concise", "auto"))
        elif response_length < 500:
            preferences.append(("style", "response_length", "moderate", "auto"))
        else:
            preferences.append(("style", "response_length", "detailed", "auto"))
        
        if "图表" in response or "chart" in response.lower():
            preferences.append(("content", "chart_preference", "prefers_charts", "auto"))
        
        if "```" in response:
            preferences.append(("style", "code_preference", "prefers_code_blocks", "auto"))
        
        if "分析" in query or "分析" in response:
            preferences.append(("content", "analysis_preference", "prefers_analysis", "auto"))
        
        for pref in preferences:
            self.save_user_preference(user_id, pref[0], pref[1], pref[2], pref[3])
        
        return [p[1] for p in preferences]
    
    # ==================== 成功案例层 ====================
    
    def save_success_case(
        self,
        user_id: Optional[int],
        query: str,
        response: str,
        tool_calls: List[Dict] = None,
        chart_generated: bool = False
    ) -> SuccessCase:
        """保存成功案例"""
        query_intent = self._classify_intent(query)
        keywords = self._extract_keywords(query)
        tool_sequence = [tc.get("name") for tc in tool_calls] if tool_calls else []
        
        success_case = SuccessCase(
            user_id=user_id,
            query_pattern=query[:255],
            query_intent=query_intent,
            original_query=query,
            successful_response=response,
            tool_calls=tool_calls,
            tool_sequence=tool_sequence,
            chart_generated=chart_generated,
            chart_types=self._extract_chart_types(response),
            keywords=keywords,
            satisfaction_score=1.0
        )
        
        self.db.add(success_case)
        self.db.commit()
        return success_case
    
    def get_success_cases(
        self,
        query: str,
        user_id: Optional[int] = None,
        limit: int = 3
    ) -> List[SuccessCase]:
        """获取相关成功案例"""
        keywords = self._extract_keywords(query)
        query_intent = self._classify_intent(query)
        
        query_obj = self.db.query(SuccessCase).filter(
            SuccessCase.satisfaction_score >= 0.8
        )
        
        if user_id:
            query_obj = query_obj.filter(
                or_(SuccessCase.user_id == user_id, SuccessCase.user_id == None)
            )
        
        cases = query_obj.order_by(
            desc(SuccessCase.satisfaction_score),
            desc(SuccessCase.reuse_count)
        ).limit(limit * 2).all()
        
        scored_cases = []
        for case in cases:
            score = self._calculate_relevance(case, keywords, query_intent)
            scored_cases.append((case, score))
        
        scored_cases.sort(key=lambda x: x[1], reverse=True)
        
        selected_cases = [c[0] for c in scored_cases[:limit]]
        for case in selected_cases:
            case.reuse_count = (case.reuse_count or 0) + 1
        self.db.commit()
        
        return selected_cases
    
    # ==================== 失败教训层 ====================
    
    def save_failure_lesson(
        self,
        user_id: Optional[int],
        query: str,
        failed_response: str,
        user_correction: str,
        failure_type: str = "general"
    ) -> FailureLesson:
        """保存失败教训"""
        failure_reason = self._extract_failure_reason(failed_response, user_correction)
        correct_approach = self._extract_correct_approach(user_correction)
        
        lesson = FailureLesson(
            user_id=user_id,
            query_pattern=query[:255],
            original_query=query,
            failed_response=failed_response,
            failure_reason=failure_reason,
            user_correction=user_correction,
            correct_approach=correct_approach,
            failure_type=failure_type,
            occurrence_count=1
        )
        
        self.db.add(lesson)
        self.db.commit()
        return lesson
    
    def get_failure_lessons(
        self,
        query: str,
        user_id: Optional[int] = None,
        limit: int = 3
    ) -> List[FailureLesson]:
        """获取相关失败教训"""
        keywords = self._extract_keywords(query)
        
        query_obj = self.db.query(FailureLesson).filter(
            FailureLesson.active == True
        )
        
        if user_id:
            query_obj = query_obj.filter(
                or_(FailureLesson.user_id == user_id, FailureLesson.user_id == None)
            )
        
        lessons = query_obj.order_by(
            desc(FailureLesson.importance_score),
            desc(FailureLesson.occurrence_count)
        ).limit(limit * 2).all()
        
        scored_lessons = []
        for lesson in lessons:
            score = self._calculate_lesson_relevance(lesson, keywords)
            scored_lessons.append((lesson, score))
        
        scored_lessons.sort(key=lambda x: x[1], reverse=True)
        
        return [l[0] for l in scored_lessons[:limit]]
    
    # ==================== 记忆注入 ====================
    
    def build_memory_context(
        self,
        user_id: Optional[int],
        query: str
    ) -> str:
        """构建记忆上下文，按优先级注入到系统提示词"""
        context_parts = []
        
        preferences = self.get_user_preferences(user_id, limit=5)
        if preferences:
            pref_lines = []
            for pref in preferences:
                pref_lines.append(f"- {pref.preference_key}: {pref.preference_value}")
            context_parts.append("【用户偏好】\n" + "\n".join(pref_lines))
        
        success_cases = self.get_success_cases(query, user_id, limit=2)
        if success_cases:
            case_lines = []
            for i, case in enumerate(success_cases, 1):
                tool_seq = " → ".join(case.tool_sequence) if case.tool_sequence else "无工具调用"
                case_lines.append(f"案例{i}: {case.query_pattern[:50]}...")
                case_lines.append(f"  成功路径: {tool_seq}")
            context_parts.append("【成功案例参考】\n" + "\n".join(case_lines))
        
        failure_lessons = self.get_failure_lessons(query, user_id, limit=2)
        if failure_lessons:
            lesson_lines = []
            for lesson in failure_lessons:
                lesson_lines.append(f"- 避免: {lesson.failure_reason[:80]}")
                if lesson.correct_approach:
                    lesson_lines.append(f"  正确做法: {lesson.correct_approach[:80]}")
            context_parts.append("【避免的错误】\n" + "\n".join(lesson_lines))
        
        if context_parts:
            return "\n\n".join(context_parts)
        return ""
    
    # ==================== 辅助方法 ====================
    
    def _classify_intent(self, query: str) -> str:
        """分类问题意图"""
        query_lower = query.lower()
        
        if any(kw in query for kw in ["快照", "数据集", "表结构", "字段结构"]):
            return "schema_query"
        if any(kw in query for kw in ["图表", "柱状图", "折线图", "饼图", "直方图", "散点图"]):
            return "chart_generation"
        if any(kw in query for kw in ["分析", "统计", "趋势", "分布"]):
            return "data_analysis"
        if any(kw in query for kw in ["查询", "列出", "显示", "查看"]):
            return "data_query"
        
        return "general"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        patterns = [
            r'影像|镜头|DXO|评分|数据',
            r'图表|柱状图|折线图|饼图|直方图',
            r'分析|统计|趋势|分布',
            r'快照|数据集',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            keywords.extend(matches)
        
        return list(set(keywords))
    
    def _extract_chart_types(self, response: str) -> List[str]:
        """提取图表类型"""
        chart_types = []
        chart_keywords = {
            "bar": ["柱状图", "bar", "条形图"],
            "line": ["折线图", "line", "趋势图"],
            "pie": ["饼图", "pie", "占比图"],
            "histogram": ["直方图", "histogram", "分布图"],
            "scatter": ["散点图", "scatter"]
        }
        
        response_lower = response.lower()
        for chart_type, keywords in chart_keywords.items():
            if any(kw in response_lower for kw in keywords):
                chart_types.append(chart_type)
        
        return chart_types
    
    def _extract_failure_reason(self, failed_response: str, correction: str) -> str:
        """提取失败原因"""
        if "字段" in correction and ("错误" in correction or "不存在" in correction):
            return "使用了错误的字段名"
        if "先" in correction and ("查询" in correction or "获取" in correction):
            return "跳过了数据理解步骤"
        if "图表" in correction and "结论" in correction:
            return "只生成图表未给出分析结论"
        
        return correction[:100] if correction else "未知原因"
    
    def _extract_correct_approach(self, correction: str) -> str:
        """提取正确做法"""
        if not correction:
            return ""
        
        sentences = re.split(r'[。！？\n]', correction)
        for sentence in sentences:
            if any(kw in sentence for kw in ["应该", "需要", "先", "建议"]):
                return sentence[:100]
        
        return correction[:100]
    
    def _calculate_relevance(
        self,
        case: SuccessCase,
        keywords: List[str],
        query_intent: str
    ) -> float:
        """计算成功案例相关性"""
        score = 0.0
        
        if case.keywords:
            case_keywords = case.keywords if isinstance(case.keywords, list) else []
            common_keywords = set(keywords) & set(case_keywords)
            score += len(common_keywords) * 0.3
        
        if case.query_intent == query_intent:
            score += 0.4
        
        score += (case.satisfaction_score or 0) * 0.2
        score += min((case.reuse_count or 0) * 0.05, 0.2)
        
        return score
    
    def _calculate_lesson_relevance(
        self,
        lesson: FailureLesson,
        keywords: List[str]
    ) -> float:
        """计算失败教训相关性"""
        score = 0.0
        
        if lesson.query_pattern:
            for kw in keywords:
                if kw in lesson.query_pattern:
                    score += 0.2
        
        score += (lesson.importance_score or 0) * 0.3
        score += min((lesson.occurrence_count or 0) * 0.1, 0.3)
        
        return score


memory_service = MemoryService()
