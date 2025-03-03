package com.hyunjin.analyzer_api.result.service;

import com.hyunjin.analyzer_api.result.dto.ResultDetailResponse;
import com.hyunjin.analyzer_api.result.dto.ResultResponse;
import com.hyunjin.analyzer_api.result.model.AnalysisResult;
import com.hyunjin.analyzer_api.result.repository.ResultRepository;
import com.hyunjin.analyzer_api.result.vo.AnalysisContent;
import com.hyunjin.analyzer_api.result.vo.SummaryContent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.nio.channels.FileChannel;
import java.time.LocalDateTime;
import java.util.NoSuchElementException;
import java.util.Optional;

@Slf4j
@Service
@RequiredArgsConstructor
public class ResultService {
    private final ResultRepository resultRepository;

    public void saveResult(ResultResponse resultResponse) {
        // 값 객체 생성
        AnalysisContent analysisContent = AnalysisContent.fromEncodedString(resultResponse);
        SummaryContent summaryContent = SummaryContent.fromEncodedString(resultResponse);

        // AnalysisResult 생성
        AnalysisResult result = AnalysisResult.builder()
                .projectId(resultResponse.getProjectId())
                .success(resultResponse.isSuccess())
                .error(resultResponse.isSuccess() ? null : resultResponse.getError())
                .analysisContent(analysisContent)
                .summaryContent(summaryContent)
                .filesProcessed(resultResponse.getFilesProcessed())
                .timestamp(LocalDateTime.now())
                .build();

        resultRepository.save(result);
    }

    public ResultDetailResponse findResultByProjectId(String projectId) {
        return resultRepository.findByProjectId(projectId)
                .map(result -> ResultDetailResponse.builder()
                        .projectId(result.projectId())
                        .success(result.success())
                        .error(result.error())
                        .analysisContent(result.analysisContent().toString())
                        .summaryContent(result.summaryContent().toString())
                        .filesProcessed(result.filesProcessed())
                        .timestamp(result.timestamp())
                        .build()).orElseThrow(NoSuchElementException::new);
    }
}
