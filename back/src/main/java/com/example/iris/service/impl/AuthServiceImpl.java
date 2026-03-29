package com.example.iris.service.impl;

import com.example.iris.common.PasswordUtil;
import com.example.iris.dto.AccountInfo;
import com.example.iris.dto.ChangePasswordRequest;
import com.example.iris.dto.LoginRequest;
import com.example.iris.dto.RegisterRequest;
import com.example.iris.entity.Account;
import com.example.iris.mapper.AccountMapper;
import com.example.iris.service.AuthService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
/**
 * 文件说明：AuthServiceImpl 文件，承载该模块的核心职责与对外行为。
 * 函数概览：AuthServiceImpl、register、login、changePassword。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class AuthServiceImpl implements AuthService {

    private static final Logger log = LoggerFactory.getLogger(AuthServiceImpl.class);

    private final AccountMapper accountMapper;

    /**
     * 函数作用：AuthServiceImpl，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public AuthServiceImpl(AccountMapper accountMapper) {
        this.accountMapper = accountMapper;
    }

    @Override
    /**
     * 函数作用：register，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public AccountInfo register(RegisterRequest request) {
        log.info("开始注册账号，username={}", request.getUsername());
        Account existed = accountMapper.selectByUsername(request.getUsername());
        if (existed != null) {
            log.warn("注册失败：账号已存在，username={}", request.getUsername());
            throw new IllegalArgumentException("账号已存在");
        }

        String salt = PasswordUtil.generateSalt(16);
        String hash = PasswordUtil.hashPassword(request.getPassword(), salt);
        Account account = Account.builder()
                .username(request.getUsername())
                .passwordSalt(salt)
                .passwordHash(hash)
                .build();

        int rows = accountMapper.insert(account);
        if (rows <= 0 || account.getId() == null) {
            log.error("注册失败：插入影响行数={}", rows);
            throw new RuntimeException("注册失败，请稍后重试");
        }

        log.info("注册成功：username={}, id={}", request.getUsername(), account.getId());
        return AccountInfo.builder()
                .id(account.getId())
                .username(account.getUsername())
                .createdAt(account.getCreatedAt())
                .build();
    }

    @Override
    /**
     * 函数作用：login，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public AccountInfo login(LoginRequest request) {
        log.info("开始登录认证，username={}", request.getUsername());
        Account account = accountMapper.selectByUsername(request.getUsername());
        if (account == null) {
            log.warn("登录失败：账号不存在，username={}", request.getUsername());
            throw new IllegalArgumentException("用户名或密码错误");
        }

        boolean ok = PasswordUtil.verifyPassword(
                request.getPassword(),
                account.getPasswordSalt(),
                account.getPasswordHash()
        );
        if (!ok) {
            log.warn("登录失败：密码不匹配，username={}", request.getUsername());
            throw new IllegalArgumentException("用户名或密码错误");
        }

        log.info("登录成功：username={}, id={}", account.getUsername(), account.getId());
        return AccountInfo.builder()
                .id(account.getId())
                .username(account.getUsername())
                .createdAt(account.getCreatedAt())
                .build();
    }

    @Override
    /**
     * 函数作用：changePassword，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public void changePassword(Long accountId, ChangePasswordRequest request) {
        log.info("开始修改密码，accountId={}", accountId);
        Account account = accountMapper.selectById(accountId);
        if (account == null) {
            log.warn("修改密码失败：账号不存在，accountId={}", accountId);
            throw new IllegalArgumentException("账号不存在");
        }

        boolean ok = PasswordUtil.verifyPassword(
                request.getOldPassword(),
                account.getPasswordSalt(),
                account.getPasswordHash()
        );
        if (!ok) {
            log.warn("修改密码失败：旧密码错误，accountId={}", accountId);
            throw new IllegalArgumentException("旧密码错误");
        }

        if (request.getOldPassword().equals(request.getNewPassword())) {
            throw new IllegalArgumentException("新密码不能与旧密码相同");
        }

        String newSalt = PasswordUtil.generateSalt(16);
        String newHash = PasswordUtil.hashPassword(request.getNewPassword(), newSalt);
        int rows = accountMapper.updatePasswordById(accountId, newSalt, newHash);
        if (rows <= 0) {
            log.error("修改密码失败：更新影响行数={}", rows);
            throw new RuntimeException("修改密码失败，请稍后重试");
        }

        log.info("修改密码成功，accountId={}", accountId);
    }
}
