package com.example.iris.service;

import com.example.iris.dto.AccountInfo;
import com.example.iris.dto.ChangePasswordRequest;
import com.example.iris.dto.LoginRequest;
import com.example.iris.dto.RegisterRequest;

/**
 * 文件说明：AuthService 文件，承载该模块的核心职责与对外行为。
 * 函数概览：见各方法注释。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public interface AuthService {

    AccountInfo register(RegisterRequest request);

    AccountInfo login(LoginRequest request);

    void changePassword(Long accountId, ChangePasswordRequest request);
}
