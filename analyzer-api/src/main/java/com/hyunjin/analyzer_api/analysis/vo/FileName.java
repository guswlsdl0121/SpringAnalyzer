package com.hyunjin.analyzer_api.analysis.vo;

import lombok.Value;
import org.springframework.web.multipart.MultipartFile;

@Value
public class FileName {
    String name;
    String extension;
    String originalValue;

    private FileName(String originalValue) {
        this.originalValue = originalValue;

        int lastDotIndex = originalValue.lastIndexOf('.');
        this.name = originalValue.substring(0, lastDotIndex);
        this.extension = originalValue.substring(lastDotIndex + 1);
    }

    public static FileName fromFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("ZIP 파일을 업로드해주세요");
        }

        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || !originalFilename.endsWith(".zip")) {
            throw new IllegalArgumentException("유효한 ZIP 파일만 지원됩니다");
        }

        return new FileName(originalFilename);
    }
}