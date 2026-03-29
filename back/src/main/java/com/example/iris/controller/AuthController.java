package com.example.iris.controller;

import com.example.iris.common.Result;
import com.example.iris.dto.AccountInfo;
import com.example.iris.dto.ChangePasswordRequest;
import com.example.iris.dto.LoginRequest;
import com.example.iris.dto.RegisterRequest;
import com.example.iris.service.AuthService;
import jakarta.servlet.http.HttpSession;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/auth")
/**
 * 文件说明：AuthController 文件，承载该模块的核心职责与对外行为。
 * 函数概览：AuthController、register、login、changePassword、logout。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class AuthController {

    private static final Logger log = LoggerFactory.getLogger(AuthController.class);
    private static final String SESSION_KEY_ACCOUNT = "SESSION_KEY_ACCOUNT";

    private final AuthService authService;

    /**
     * 函数作用：AuthController，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/register")
    /**
     * 函数作用：register，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<AccountInfo> register(@Valid @RequestBody RegisterRequest request) {
        log.info("接收到注册请求，username={}", request.getUsername());
        return Result.success(authService.register(request));
    }

    @PostMapping("/login")
    /**
     * 函数作用：login，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<AccountInfo> login(@Valid @RequestBody LoginRequest request, HttpSession session) {
        log.info("接收到登录请求，username={}", request.getUsername());
        AccountInfo info = authService.login(request);
        session.setAttribute(SESSION_KEY_ACCOUNT, info);
        log.info("登录成功，username={}, id={}", info.getUsername(), info.getId());
        return Result.success(info);
    }

    @PostMapping("/change-password")
    /**
     * 函数作用：changePassword，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<Void> changePassword(@Valid @RequestBody ChangePasswordRequest request, HttpSession session) {
        AccountInfo accountInfo = (AccountInfo) session.getAttribute(SESSION_KEY_ACCOUNT);
        if (accountInfo == null) {
            throw new IllegalArgumentException("请先登录");
        }

        log.info("接收到修改密码请求，accountId={}", accountInfo.getId());
        authService.changePassword(accountInfo.getId(), request);
        return Result.success();
    }

    @PostMapping("/logout")
    /**
     * 函数作用：logout，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<Void> logout(HttpSession session) {
        log.info("接收到退出请求");
        session.invalidate();
        return Result.success();
    }
}
