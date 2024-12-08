import re
import streamlit as st
import plotly.express as px
from collections import Counter

st.set_page_config(page_title="텍스트 분석기", page_icon="📝", layout="wide")

# CSS 스타일
st.markdown("""
<style>
    .result-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
    .error {
        color: #dc3545;
        text-decoration: line-through;
    }
    .correction {
        color: #28a745;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class TextAnalyzer:
    def __init__(self, text):
        self.text = text
        self.sentences = self._split_sentences()

    def _split_sentences(self):
        return re.split(r'[.!?]\s*', self.text)

    def get_char_count(self):
        total = len(self.text)
        no_spaces = len(self.text.replace(" ", ""))
        return total, no_spaces

    def get_word_count(self):
        korean = len(re.findall(r'[가-힣]+', self.text))
        english = len(re.findall(r'[a-zA-Z]+', self.text))
        return korean, english

    def get_char_types(self):
        return {
            '한글': len(re.findall(r'[가-힣]', self.text)),
            '영어': len(re.findall(r'[a-zA-Z]', self.text)),
            '숫자': len(re.findall(r'[0-9]', self.text)),
            '공백': len(re.findall(r'\s', self.text)),
            '특수문자': len(re.findall(r'[^가-힣a-zA-Z0-9\s]', self.text))
        }

class SpacingChecker:
    def __init__(self):
        # 띄어쓰기 규칙을 외부 파일에서 읽어오도록 개선 (rules.txt 파일 필요)
        with open('rules.txt', 'r', encoding='utf-8') as f:
            self.spacing_rules = {}
            for line in f:
                if line.strip() and not line.startswith('#'):
                    pattern, replacement = line.strip().split(',')
                    self.spacing_rules[pattern] = replacement

    def check(self, text):
        suggestions = []
        offset = 0  # 띄어쓰기 교정으로 인한 텍스트 길이 변화를 반영하기 위한 변수
        for pattern, replacement in self.spacing_rules.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                original = match.group(0)
                corrected = re.sub(pattern, replacement, original)
                if original != corrected:
                    suggestions.append({
                        'original': original,
                        'corrected': corrected,
                        'start': match.start() + offset,  # offset을 더하여 start 위치 보정
                        'end': match.end() + offset    # offset을 더하여 end 위치 보정
                    })
                    offset += len(corrected) - len(original)  # 띄어쓰기 추가로 인해 텍스트 길이가 늘어난 만큼 offset 증가
        return suggestions

def main():
    st.title("📝 텍스트 분석기")
    st.markdown("#### 텍스트를 입력하시면 다양한 분석 결과를 보여드립니다.")

    text = st.text_area(
        "분석할 텍스트를 입력하세요",
        height=200,
        placeholder="텍스트를 입력하시면 문자 수, 단어 수, 문장 수 등을 분석해드립니다..."
    )

    if st.button('분석하기', use_container_width=True):
        if not text:
            st.warning('텍스트를 입력해주세요.')
            return

        analyzer = TextAnalyzer(text)
        checker = SpacingChecker()

        # ... (기본 통계, 문자 종류별 분석) ...

        # 띄어쓰기 분석
        st.markdown("### 🔍 띄어쓰기 분석")
        spacing_suggestions = checker.check(text)

        if spacing_suggestions:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("#### 띄어쓰기 제안:")
            for suggestion in spacing_suggestions:
                st.markdown(f"- <span class='error'>{suggestion['original']}</span> → "
                            f"<span class='correction'>{suggestion['corrected']}</span>",
                            unsafe_allow_html=True)

            corrected_text = text
            for suggestion in reversed(spacing_suggestions):  # reversed() 함수를 사용하여 뒤에서부터 교정
                start, end = suggestion['start'], suggestion['end']
                corrected_text = corrected_text[:start] + suggestion['corrected'] + corrected_text[end:]

            if st.button('교정된 텍스트 보기'):
                st.text_area("교정된 텍스트:", corrected_text, height=200)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("기본적인 띄어쓰기 검사에서 특이사항이 발견되지 않았습니다.")

    # ... (블로그 링크 섹션) ...

if __name__ == '__main__':
    main()
