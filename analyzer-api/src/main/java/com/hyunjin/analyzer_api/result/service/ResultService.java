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

import java.time.LocalDateTime;
import java.util.NoSuchElementException;

@Slf4j
@Service
@RequiredArgsConstructor
public class ResultService {
    private final ResultRepository resultRepository;

    /**
     * 분석 결과를 저장합니다.
     *
     * @param resultResponse 저장할 분석 결과 응답 객체
     */
    public void saveResult(ResultResponse resultResponse) {
        // 인코딩된 문자열로부터 분석 내용과 요약 내용 값 객체 생성
        AnalysisContent analysisContent = AnalysisContent.fromEncodedString(resultResponse);
        SummaryContent summaryContent = SummaryContent.fromEncodedString(resultResponse);

        // AnalysisResult 엔티티 생성
        AnalysisResult result = AnalysisResult.builder()
                .projectId(resultResponse.getProjectId())
                .success(resultResponse.isSuccess())
                .error(resultResponse.isSuccess() ? null : resultResponse.getError())
                .analysisContent(analysisContent)
                .summaryContent(summaryContent)
                .filesProcessed(resultResponse.getFilesProcessed())
                .timestamp(LocalDateTime.now())
                .build();

        // 생성된 AnalysisResult 엔티티를 저장소에 저장
        resultRepository.save(result);
    }

    /**
     * 프로젝트 ID로 분석 결과를 조회합니다.
     *
     * @param projectId 조회할 프로젝트 ID
     * @return 조회된 분석 결과의 상세 응답 객체
     * @throws NoSuchElementException 해당 프로젝트 ID의 결과가 없을 경우 발생
     */
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
                        .build())
                .orElseThrow(NoSuchElementException::new);
    }
}
