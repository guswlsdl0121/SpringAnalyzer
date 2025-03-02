package com.hyunjin.analyzer_api.analysis.vo;

import lombok.Value;
import org.springframework.web.multipart.MultipartFile;

/**
 * 파일 이름을 처리하기 위한 Value Object.
 * 원본 파일명, 확장자 제외한 이름, 확장자를 분리하여 저장합니다.
 */
@Value
public class FileName {
    String name;            // 확장자를 제외한 파일 이름
    String extension;   // 파일 확장자
    String originalValue;   // 원본 파일명

    private FileName(String originalValue) {
        this.originalValue = originalValue;

        int lastDotIndex = originalValue.lastIndexOf('.');
        this.name = originalValue.substring(0, lastDotIndex);
        this.extension = originalValue.substring(lastDotIndex + 1);
    }

    /**
     * MultipartFile로부터 FileName 객체를 생성합니다.
     * 파일이 비어있거나 ZIP 형식이 아닌 경우 예외를 발생시킵니다.
     *
     * @param file 업로드된 MultipartFile 객체
     * @return 새로운 FileName 객체
     * @throws IllegalArgumentException 파일이 없거나 ZIP 형식이 아닐 경우
     */
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
