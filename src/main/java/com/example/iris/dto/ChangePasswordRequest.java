package com.example.iris.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
/**
 * 文件说明：ChangePasswordRequest 文件，承载该模块的核心职责与对外行为。
 * 函数概览：见各方法注释。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class ChangePasswordRequest {

    @NotBlank(message = "旧密码不能为空")
    private String oldPassword;

    @NotBlank(message = "新密码不能为空")
    @Size(min = 6, max = 100, message = "新密码长度必须在 6~100 之间")
    private String newPassword;
}
