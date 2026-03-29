package com.example.iris.common;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
/**
 * 文件说明：Result 文件，承载该模块的核心职责与对外行为。
 * 函数概览：success、success、fail。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class Result<T> {

    private Integer code;
    private String msg;
    private T data;

    /**
     * 函数作用：success，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public static <T> Result<T> success(T data) {
        return Result.<T>builder()
                .code(200)
                .msg("操作成功")
                .data(data)
                .build();
    }

    /**
     * 函数作用：success，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public static Result<Void> success() {
        return Result.<Void>builder()
                .code(200)
                .msg("操作成功")
                .data(null)
                .build();
    }

    /**
     * 函数作用：fail，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public static Result<Void> fail(Integer code, String msg) {
        return Result.<Void>builder()
                .code(code)
                .msg(msg)
                .data(null)
                .build();
    }
}
