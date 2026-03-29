package com.example.iris.common;

import jakarta.validation.ConstraintViolationException;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.resource.NoResourceFoundException;

@RestControllerAdvice
/**
 * 文件说明：GlobalExceptionHandler 文件，承载该模块的核心职责与对外行为。
 * 函数概览：handleMethodArgumentNotValidException、handleBindException、handleConstraintViolationException、handleIllegalArgumentException、handleNoResourceFoundException、handleException。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(MethodArgumentNotValidException.class)
    /**
     * 函数作用：handleMethodArgumentNotValidException，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<Void> handleMethodArgumentNotValidException(MethodArgumentNotValidException ex) {
        String msg = ex.getBindingResult().getFieldErrors().stream()
                .map(error -> error.getDefaultMessage())
                .collect(Collectors.joining(";"));
        log.warn("请求参数校验失败：{}", msg);
        return Result.fail(400, msg);
    }

    @ExceptionHandler(BindException.class)
    /**
     * 函数作用：handleBindException，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<Void> handleBindException(BindException ex) {
        String msg = ex.getBindingResult().getFieldErrors().stream()
                .map(error -> error.getDefaultMessage())
                .collect(Collectors.joining(";"));
        log.warn("参数绑定校验失败：{}", msg);
        return Result.fail(400, msg);
    }

    @ExceptionHandler(ConstraintViolationException.class)
    /**
     * 函数作用：handleConstraintViolationException，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<Void> handleConstraintViolationException(ConstraintViolationException ex) {
        log.warn("参数约束校验失败：{}", ex.getMessage());
        return Result.fail(400, ex.getMessage());
    }

    @ExceptionHandler(IllegalArgumentException.class)
    /**
     * 函数作用：handleIllegalArgumentException，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<Void> handleIllegalArgumentException(IllegalArgumentException ex) {
        log.warn("业务参数异常：{}", ex.getMessage());
        return Result.fail(400, ex.getMessage());
    }

    @ExceptionHandler(NoResourceFoundException.class)
    /**
     * 函数作用：handleNoResourceFoundException，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<Void> handleNoResourceFoundException(NoResourceFoundException ex) {
        log.warn("资源不存在：{}", ex.getMessage());
        return Result.fail(404, "请求资源不存在");
    }

    @ExceptionHandler(Exception.class)
    /**
     * 函数作用：handleException，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<Void> handleException(Exception ex) {
        log.error("系统异常：", ex);
        return Result.fail(500, "系统异常，请联系管理员");
    }
}
