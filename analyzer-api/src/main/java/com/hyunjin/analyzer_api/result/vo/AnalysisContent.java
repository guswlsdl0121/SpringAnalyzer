package com.hyunjin.analyzer_api.result.vo;

import com.hyunjin.analyzer_api.common.util.Base64Utils;
import com.hyunjin.analyzer_api.result.dto.ResultResponse;
import lombok.Value;

/**
 * 분석 내용을 나타내는 값 객체 클래스.
 */
@Value
public class AnalysisContent {
    String content;

    private AnalysisContent(String content) {
        this.content = content;
    }

    /**
     * ResultResponse로부터 인코딩된 문자열을 디코딩하여 AnalysisContent 객체를 생성합니다.
     *
     * @param resultResponse 분석 결과 응답 객체
     * @return 생성된 AnalysisContent 객체
     */
    public static AnalysisContent fromEncodedString(ResultResponse resultResponse) {
        String encodedContent = resultResponse.getAnalysisContent();
        if (encodedContent == null || encodedContent.isEmpty()) {
            return new AnalysisContent("");
        }

        String decodedContent = Base64Utils.decodeToString(encodedContent);
        return new AnalysisContent(decodedContent);
    }

    @Override
    public String toString() {
        return content;
    }
}
