package com.example.iris.enums;

/**
 * 文件说明：SpeciesType 文件，承载该模块的核心职责与对外行为。
 * 函数概览：getValue、contains。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public enum SpeciesType {
    IRIS_SETOSA("Iris-setosa"),
    IRIS_VERSICOLOR("Iris-versicolor");

    private final String value;

    SpeciesType(String value) {
        this.value = value;
    }

    /**
     * 函数作用：getValue，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public String getValue() {
        return value;
    }

    /**
     * 函数作用：contains，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public static boolean contains(String value) {
        for (SpeciesType item : values()) {
            if (item.value.equals(value)) {
                return true;
            }
        }
        return false;
    }
}
