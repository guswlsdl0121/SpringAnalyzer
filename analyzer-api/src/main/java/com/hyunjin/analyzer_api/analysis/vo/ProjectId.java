package com.hyunjin.analyzer_api.analysis.vo;

import lombok.Value;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;


@Value
public class ProjectId {
    String id;

    private ProjectId(String id) {
        this.id = id;
    }

    public static ProjectId fromFileName(FileName fileName) {
        String id = fileName.getName() + "_" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        return new ProjectId(id);
    }
}