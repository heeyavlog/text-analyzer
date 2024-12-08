import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re
from collections import Counter

# 페이지 설정
st.set_page_config(
   page_title="텍스트 분석기",
   page_icon="📝",
   layout="wide"
)

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
</style>
""", unsafe_allow_html=True)

def count_chars(text):
   """전체 글자 수 세기"""
   total_chars = len(text)
   chars_without_spaces = len(text.replace(" ", ""))
   return total_chars, chars_without_spaces

def count_words(text):
   """단어 수 세기"""
   # 한글 단어
   korean_words = len(re.findall(r'[가-힣]+', text))
   # 영어 단어
   english_words = len(re.findall(r'[a-zA-Z]+', text))
   return korean_words, english_words

def analyze_spacing(text):
    """띄어쓰기 분석 및 교정"""
    original_text = text
    suggestions = []
    
    # 자주 틀리는 패턴과 교정
    patterns = {
        r'([가-힣]+)때문에': r'\1 때문에',
        r'([가-힣]+)같은': r'\1 같은',
        r'수있': '수 있',
        r'것을': '걸',
        r'([가-힣]+)스러워': r'\1스러워'
    }
    
    corrected_text = text
    for pattern, correction in patterns.items():
        if re.search(pattern, text):
            # 틀린 부분 찾기
            found = re.finditer(pattern, text)
            for match in found:
                wrong_text = match.group(0)
                correct_text = re.sub(pattern, correction, wrong_text)
                suggestions.append({
                    'wrong': wrong_text,
                    'correct': correct_text,
                    'position': match.span()
                })
                corrected_text = corrected_text.replace(wrong_text, correct_text)
    
    return suggestions, corrected_text

def main():
   st.title("📝 텍스트 분석기")
   st.markdown("#### 텍스트를 입력하시면 다양한 분석 결과를 보여드립니다.")
   
   # 텍스트 입력
   text = st.text_area(
       "분석할 텍스트를 입력하세요",
       height=200,
       placeholder="여기에 텍스트를 입력해주세요..."
   )
   
   if st.button('분석하기', use_container_width=True):
       if not text:
           st.warning('텍스트를 입력해주세요.')
           return
           
       # 기본 통계
       col1, col2, col3, col4 = st.columns(4)
       
       total_chars, chars_without_spaces = count_chars(text)
       korean_words, english_words = count_words(text)
       lines = count_lines(text)
       
       with col1:
           st.markdown('<div class="result-card">', unsafe_allow_html=True)
           st.markdown("### 전체 글자 수")
           st.markdown(f'<p class="stat-value">{total_chars:,}자</p>', unsafe_allow_html=True)
           st.markdown(f'(공백 제외: {chars_without_spaces:,}자)')
           st.markdown('</div>', unsafe_allow_html=True)
           
       with col2:
           st.markdown('<div class="result-card">', unsafe_allow_html=True)
           st.markdown("### 단어 수")
           st.markdown(f'<p class="stat-value">{korean_words + english_words:,}개</p>', unsafe_allow_html=True)
           st.markdown(f'(한글: {korean_words:,}, 영어: {english_words:,})')
           st.markdown('</div>', unsafe_allow_html=True)
           
       with col3:
           st.markdown('<div class="result-card">', unsafe_allow_html=True)
           st.markdown("### 줄 수")
           st.markdown(f'<p class="stat-value">{lines:,}줄</p>', unsafe_allow_html=True)
           st.markdown('</div>', unsafe_allow_html=True)
           
       with col4:
           st.markdown('<div class="result-card">', unsafe_allow_html=True)
           st.markdown("### 문장 수")
           sentences = len(re.split(r'[.!?]+', text))
           st.markdown(f'<p class="stat-value">{sentences:,}문장</p>', unsafe_allow_html=True)
           st.markdown('</div>', unsafe_allow_html=True)
           
       # 문자 종류별 분석
       st.markdown("### 📊 문자 종류별 분석")
       
       # 문자 종류별 카운트
       char_types = {
           '한글': len(re.findall(r'[가-힣]', text)),
           '영어': len(re.findall(r'[a-zA-Z]', text)),
           '숫자': len(re.findall(r'[0-9]', text)),
           '공백': len(re.findall(r'\s', text)),
           '특수문자': len(re.findall(r'[^가-힣a-zA-Z0-9\s]', text))
       }
       
       # 파이 차트
       fig = px.pie(
           values=list(char_types.values()),
           names=list(char_types.keys()),
           title='문자 종류별 비율'
       )
       st.plotly_chart(fig)
       
      # 띄어쓰기 분석
      st.markdown("### 🔍 띄어쓰기 분석")
      suggestions, corrected_text = analyze_spacing(text)
      if suggestions:
          st.markdown('<div class="result-card">', unsafe_allow_html=True)
          st.markdown("#### 띄어쓰기 교정 제안:")
          for suggestion in suggestions:
              st.markdown(f"- '{suggestion['wrong']}' → '{suggestion['correct']}'")
          
          if st.button('교정된 텍스트 보기'):
              st.text_area("교정된 텍스트:", corrected_text, height=200)
      else:
          st.success("기본적인 띄어쓰기 검사에서 특이사항이 발견되지 않았습니다.")
             
       # 블로그 링크 섹션
       st.markdown('---')
       st.markdown('''
       ### 🔍 더 많은 정보가 필요하신가요?
       
       텍스트 분석과 관련된 자세한 정보를 확인해보세요:
       
       - ✍️ [한글 맞춤법 가이드](https://lzhakko.tistory.com/)
       - 📚 [효과적인 글쓰기 팁](https://lzhakko.tistory.com/)
       - 💡 [텍스트 분석 활용하기](https://lzhakko.tistory.com/)
       
       더 많은 유용한 정보는 [개발하는 나무](https://lzhakko.tistory.com/)에서 확인하세요!
       ''')

if __name__ == '__main__':
   main()
