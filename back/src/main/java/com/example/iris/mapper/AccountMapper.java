package com.example.iris.mapper;

import com.example.iris.entity.Account;
import org.apache.ibatis.annotations.Param;

/**
 * 文件说明：AccountMapper 文件，承载该模块的核心职责与对外行为。
 * 函数概览：见各方法注释。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public interface AccountMapper {

    Account selectById(Long id);

    Account selectByUsername(String username);

    int insert(Account account);

    int updatePasswordById(@Param("id") Long id,
                           @Param("passwordSalt") String passwordSalt,
                           @Param("passwordHash") String passwordHash);
}
