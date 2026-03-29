package com.example.iris.dto;

import java.util.List;
import lombok.Data;

@Data
/**
 * 文件说明：IrisFilterRequest 文件，承载该模块的核心职责与对外行为。
 * 函数概览：见各方法注释。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class IrisFilterRequest {

    private Double sepalLengthMin;
    private Double sepalLengthMax;
    private Double sepalWidthMin;
    private Double sepalWidthMax;
    private Double petalLengthMin;
    private Double petalLengthMax;
    private Double petalWidthMin;
    private Double petalWidthMax;
    private List<String> speciesList;
}
