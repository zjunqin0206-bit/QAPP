package com.example.iris.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
/**
 * 文件说明：RegisterRequest 文件，承载该模块的核心职责与对外行为。
 * 函数概览：见各方法注释。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class RegisterRequest {

    @NotBlank(message = "用户名不能为空")
    @Size(max = 50, message = "用户名长度不能超过 50")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 100, message = "密码长度必须在 6~100 之间")
    private String password;
}
