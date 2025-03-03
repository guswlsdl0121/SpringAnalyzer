package com.hyunjin.analyzer_api.common.util;

import lombok.extern.slf4j.Slf4j;

import java.nio.charset.StandardCharsets;
import java.util.Base64;

@Slf4j
public class Base64Utils {

    private Base64Utils() {
    }

    /**
     * 바이트 배열을 Base64로 인코딩합니다.
     *
     * @param data 인코딩할 바이트 배열
     * @return Base64로 인코딩된 문자열
     * @throws IllegalArgumentException 입력이 null이거나 인코딩 중 오류 발생 시
     */
    public static String encodeToString(byte[] data) {
        if (data == null) {
            throw new IllegalArgumentException("인코딩할 데이터가 null입니다.");
        }

        try {
            return Base64.getEncoder().encodeToString(data);
        } catch (Exception e) {
            log.error("Base64 인코딩 중 오류 발생", e);
            throw new IllegalArgumentException("Base64 인코딩 중 오류 발생: " + e.getMessage(), e);
        }
    }

    /**
     * Base64로 인코딩된 문자열을 디코딩합니다.
     *
     * @param encodedContent Base64로 인코딩된 문자열
     * @return 디코딩된 문자열
     * @throws IllegalArgumentException 입력이 null이거나 디코딩 중 오류 발생 시
     */
    public static String decodeToString(String encodedContent) {
        if (encodedContent == null) {
            throw new IllegalArgumentException("디코딩할 문자열이 null입니다.");
        }

        try {
            byte[] decodedBytes = Base64.getDecoder().decode(encodedContent);
            return new String(decodedBytes, StandardCharsets.UTF_8);
        } catch (Exception e) {
            log.error("Base64 디코딩 중 오류 발생", e);
            throw new IllegalArgumentException("Base64 디코딩 중 오류 발생: " + e.getMessage(), e);
        }
    }
}