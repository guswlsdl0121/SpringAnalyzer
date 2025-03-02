package com.hyunjin.analyzer_api.analysis.service;

import com.hyunjin.analyzer_api.analysis.factory.AnalysisMessageFactory;
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
    private final AnalysisMessageFactory analysisMessageFactory;

    public String uploadProject(MultipartFile file) {
        FileName fileName = FileName.fromFile(file);
        ProjectId projectId = ProjectId.fromFileName(fileName);
        String message = analysisMessageFactory.createRequest(projectId, file);

        rabbitTemplate.convertAndSend(
                RabbitMQConstants.ANALYZER_EXCHANGE,
                RabbitMQConstants.ROUTING_ANALYSIS_UPLOAD,
                message
        );

        return projectId.getId();
    }
}