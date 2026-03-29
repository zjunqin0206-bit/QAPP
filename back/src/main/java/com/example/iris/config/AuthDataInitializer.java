package com.example.iris.config;

import com.example.iris.common.PasswordUtil;
import com.example.iris.entity.Account;
import com.example.iris.mapper.AccountMapper;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
/**
 * 文件说明：AuthDataInitializer 文件，承载该模块的核心职责与对外行为。
 * 函数概览：AuthDataInitializer、run、ensureAccountTable、ensureDefaultAdmin。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class AuthDataInitializer implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(AuthDataInitializer.class);

    private final DataSource dataSource;
    private final AccountMapper accountMapper;

    /**
     * 函数作用：AuthDataInitializer，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public AuthDataInitializer(DataSource dataSource, AccountMapper accountMapper) {
        this.dataSource = dataSource;
        this.accountMapper = accountMapper;
    }

    @Override
    /**
     * 函数作用：run，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public void run(ApplicationArguments args) {
        log.info("认证模块初始化开始");
        ensureAccountTable();
        ensureDefaultAdmin();
        log.info("认证模块初始化完成");
    }

    /**
     * 函数作用：ensureAccountTable，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    private void ensureAccountTable() {
        String sql = "CREATE TABLE IF NOT EXISTS tb_account (\n"
                + "  id BIGINT PRIMARY KEY AUTO_INCREMENT,\n"
                + "  username VARCHAR(50) NOT NULL,\n"
                + "  password_salt VARCHAR(128) NOT NULL,\n"
                + "  password_hash VARCHAR(256) NOT NULL,\n"
                + "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n"
                + "  UNIQUE KEY uk_username (username)\n"
                + ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n";
        try (var connection = dataSource.getConnection(); var statement = connection.createStatement()) {
            statement.execute(sql);
        } catch (Exception ex) {
            log.error("创建 tb_account 表失败：", ex);
            throw new RuntimeException("数据库初始化失败：tb_account 创建失败", ex);
        }
    }

    /**
     * 函数作用：ensureDefaultAdmin，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    private void ensureDefaultAdmin() {
        String username = "admin";
        Account existed = accountMapper.selectByUsername(username);
        if (existed != null) {
            log.info("默认 admin 账号已存在，id={}", existed.getId());
            return;
        }

        String salt = PasswordUtil.generateSalt(16);
        String hash = PasswordUtil.hashPassword("123", salt);
        Account account = Account.builder()
                .username(username)
                .passwordSalt(salt)
                .passwordHash(hash)
                .build();

        int rows = accountMapper.insert(account);
        if (rows <= 0 || account.getId() == null) {
            throw new RuntimeException("默认 admin 账号插入失败");
        }

        log.info("默认 admin 账号初始化成功：id={}", account.getId());
    }
}
