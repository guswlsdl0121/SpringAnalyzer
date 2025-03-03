package com.hyunjin.analyzer_api.analysis.service;

import com.hyunjin.analyzer_api.common.util.MessageSerializer;
import com.hyunjin.analyzer_api.analysis.vo.FileName;
import com.hyunjin.analyzer_api.analysis.vo.ProjectId;
import com.hyunjin.analyzer_api.common.messaging.constants.RabbitMQConstants;
import lombok.RequiredArgsConstructor;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class AnalysisService {
    private final RabbitTemplate rabbitTemplate;
    private final MessageSerializer messageSerializer;

    /**
     * 업로드된 프로젝트 파일을 처리하고 분석 요청 메시지를 큐에 발송합니다.
     *
     * @param file 분석할 ZIP 형태의 프로젝트 파일
     * @return 생성된 프로젝트 ID
     */
    public String uploadProject(MultipartFile file) {
        // 파일명에서 정보 추출
        FileName fileName = FileName.fromFile(file);

        // 프로젝트 ID 생성
        ProjectId projectId = ProjectId.fromFileName(fileName);

        // 분석 요청 메시지 생성
        String message = messageSerializer.serializeAnalysisRequest(projectId, file);

        // RabbitMQ를 통해 분석 요청 메시지 전송
        rabbitTemplate.convertAndSend(
                RabbitMQConstants.ANALYZER_EXCHANGE,
                RabbitMQConstants.ROUTING_ANALYSIS_UPLOAD,
                message
        );

        return projectId.getId();
    }
}