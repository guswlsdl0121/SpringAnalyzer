package com.hyunjin.analyzer_api.analysis.factory;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hyunjin.analyzer_api.analysis.vo.ProjectId;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

/**
 * 분석 요청 메시지를 생성하는 팩토리 클래스.
 * 프로젝트 정보와 파일 데이터를 포함한 메시지를 JSON 형식으로 직렬화합니다.
 */
@Component
@RequiredArgsConstructor
public class AnalysisMessageFactory {
    private final ObjectMapper objectMapper;

    /**
     * 프로젝트 분석 요청 메시지를 생성합니다.
     * 파일 데이터를 Base64로 인코딩하여 JSON 형식의 메시지로 변환합니다.
     *
     * @param projectId 프로젝트 식별자
     * @param file      분석할 프로젝트 파일
     * @return JSON 형식의 메시지 문자열
     * @throws RuntimeException 메시지 생성 중 오류 발생 시
     */
    public String createRequest(ProjectId projectId, MultipartFile file) {
        try {
            // 파일 데이터를 Base64로 인코딩
            byte[] fileData = file.getBytes();
            String encodedFile = Base64.getEncoder().encodeToString(fileData);

            // 메시지 데이터 준비
            Map<String, String> messageData = new HashMap<>();
            messageData.put("projectId", projectId.getId());
            messageData.put("fileContent", encodedFile);

            // JSON으로 변환하여 메시지 전송
            return objectMapper.writeValueAsString(messageData);
        } catch (IOException e) {
            throw new RuntimeException("메시지 생성 중 오류가 발생했습니다", e);
        }
    }
}