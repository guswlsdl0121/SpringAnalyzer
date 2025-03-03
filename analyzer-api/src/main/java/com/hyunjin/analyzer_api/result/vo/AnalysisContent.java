package com.hyunjin.analyzer_api.result.vo;

import com.hyunjin.analyzer_api.common.util.Base64Utils;
import com.hyunjin.analyzer_api.result.dto.ResultResponse;
import lombok.Value;

@Value
public class AnalysisContent {
    String content;

    private AnalysisContent(String content) {
        this.content = content;
    }

    public static AnalysisContent fromEncodedString(ResultResponse resultResponse) {
        String encodedContent = resultResponse.getAnalysisContent();
        if (encodedContent == null || encodedContent.isEmpty()) {
            return empty();
        }

        String decodedContent = Base64Utils.decodeToString(encodedContent);
        return new AnalysisContent(decodedContent);
    }

    public static AnalysisContent fromString(String content) {
        if (content == null || content.isEmpty()) {
            return empty();
        }
        return new AnalysisContent(content);
    }

    public static AnalysisContent empty() {
        return new AnalysisContent("");
    }

    public boolean hasContent() {
        return content != null && !content.isEmpty();
    }

    @Override
    public String toString() {
        return content;
    }
}