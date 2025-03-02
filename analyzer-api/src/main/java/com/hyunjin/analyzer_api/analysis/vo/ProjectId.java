package com.hyunjin.analyzer_api.analysis.vo;

import lombok.Value;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;


/**
 * 프로젝트 식별자를 관리하는 Value Object.
 * 파일명과 타임스탬프를 조합하여 고유한 ID를 생성합니다.
 */
@Value
public class ProjectId {
    String id; // 프로젝트 고유 식별자

    private ProjectId(String id) {
        this.id = id;
    }

    /**
     * FileName 객체로부터 프로젝트 ID를 생성합니다.
     * 파일명과 현재 시간을 조합하여 고유한 ID를 생성합니다.
     *
     * @param fileName 파일명 객체
     * @return 새로운 ProjectId 객체
     */
    public static ProjectId fromFileName(FileName fileName) {
        String id = fileName.getName() + "_" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        return new ProjectId(id);
    }
}