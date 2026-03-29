package com.example.iris.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
/**
 * 文件说明：IrisRequest 文件，承载该模块的核心职责与对外行为。
 * 函数概览：见各方法注释。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class IrisRequest {

    @NotNull(message = "花萼长度不能为空")
    private Double sepalLength;

    @NotNull(message = "花萼宽度不能为空")
    private Double sepalWidth;

    @NotNull(message = "花瓣长度不能为空")
    private Double petalLength;

    @NotNull(message = "花瓣宽度不能为空")
    private Double petalWidth;

    @NotBlank(message = "品种不能为空")
    private String species;
}
