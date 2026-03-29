package com.example.iris.dto;

import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
/**
 * 文件说明：AccountInfo 文件，承载该模块的核心职责与对外行为。
 * 函数概览：见各方法注释。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class AccountInfo {

    private Long id;
    private String username;
    private LocalDateTime createdAt;
}
