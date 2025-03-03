package com.hyunjin.analyzer_api.result.vo;

import com.hyunjin.analyzer_api.common.util.Base64Utils;
import com.hyunjin.analyzer_api.result.dto.ResultResponse;
import lombok.Value;

@Value
public class SummaryContent {
    String content;

    private SummaryContent(String content) {
        this.content = content;
    }

    public static SummaryContent fromEncodedString(ResultResponse resultResponse) {
        String encodedContent = resultResponse.getSummaryContent();
        if (encodedContent == null || encodedContent.isEmpty()) {
            return empty();
        }

        String decodedContent = Base64Utils.decodeToString(encodedContent);
        return new SummaryContent(decodedContent);
    }

    public static SummaryContent fromString(String content) {
        if (content == null || content.isEmpty()) {
            return empty();
        }
        return new SummaryContent(content);
    }

    public static SummaryContent empty() {
        return new SummaryContent("");
    }

    public boolean hasContent() {
        return content != null && !content.isEmpty();
    }

    @Override
    public String toString() {
        return content;
    }
}