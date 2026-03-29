package com.example.iris.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
/**
 * 文件说明：LoginRequest 文件，承载该模块的核心职责与对外行为。
 * 函数概览：见各方法注释。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class LoginRequest {

    @NotBlank(message = "用户名不能为空")
    private String username;

    @NotBlank(message = "密码不能为空")
    private String password;
}
