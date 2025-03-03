package com.hyunjin.analyzer_api.common.util;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.hyunjin.analyzer_api.analysis.vo.ProjectId;
import com.hyunjin.analyzer_api.result.dto.ResultResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class MessageSerializer {
    private final ObjectMapper objectMapper;

    /**
     * 분석 요청 메시지를 생성합니다.
     * 프로젝트 ID와 ZIP 파일을 이용해 메시지를 생성하고 JSON 형식으로 직렬화합니다.
     *
     * @param projectId 프로젝트 식별자
     * @param file      분석할 프로젝트 ZIP 파일
     * @return JSON 형식의 메시지 문자열
     * @throws RuntimeException 메시지 생성 중 오류 발생 시
     */
    public String serializeAnalysisRequest(ProjectId projectId, MultipartFile file) {
        try {
            // 파일 데이터를 Base64로 인코딩
            byte[] fileData = file.getBytes();
            String encodedFile = Base64Utils.encodeToString(fileData);

            // 메시지 데이터 준비
            Map<String, String> messageData = new HashMap<>();
            messageData.put("projectId", projectId.getId());
            messageData.put("fileContent", encodedFile);

            // JSON으로 변환하여 메시지 전송
            return objectMapper.writeValueAsString(messageData);
        } catch (IOException e) {
            log.error("분석 요청 메시지 직렬화 중 오류 발생", e);
            throw new RuntimeException("메시지 생성 중 오류가 발생했습니다", e);
        }
    }

    /**
     * JSON 메시지를 ResultResponse 객체로 역직렬화합니다.
     *
     * @param message JSON 형식의 결과 메시지
     * @return 역직렬화된 ResultResponse 객체
     * @throws RuntimeException 역직렬화 중 오류 발생 시
     */
    public ResultResponse deserializeResultResponse(String message) {
        try {
            log.debug("결과 메시지 역직렬화 시작: {}", message.substring(0, Math.min(100, message.length())));
            return objectMapper.readValue(message, ResultResponse.class);
        } catch (JsonProcessingException e) {
            log.error("결과 메시지 역직렬화 중 오류 발생", e);
            throw new RuntimeException("결과 메시지 역직렬화에 실패했습니다", e);
        }
    }
}