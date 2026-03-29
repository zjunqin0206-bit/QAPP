package com.example.iris.common;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

public final class PasswordUtil {

    private static final int ITERATIONS = 120000;
    private static final int KEY_LENGTH_BITS = 256;

    /**
     * 函数作用：PasswordUtil，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    private PasswordUtil() {
    }

    /**
     * 函数作用：generateSalt，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public static String generateSalt(int length) {
        byte[] saltBytes = new byte[length];
        new SecureRandom().nextBytes(saltBytes);
        return Base64.getEncoder().encodeToString(saltBytes);
    }

    /**
     * 函数作用：hashPassword，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public static String hashPassword(String password, String salt) {
        try {
            byte[] saltBytes = Base64.getDecoder().decode(salt);
            PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), saltBytes, ITERATIONS, KEY_LENGTH_BITS);
            SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            byte[] hashBytes = factory.generateSecret(spec).getEncoded();
            return Base64.getEncoder().encodeToString(hashBytes);
        } catch (Exception ex) {
            throw new RuntimeException("密码加密失败", ex);
        }
    }

    /**
     * 函数作用：verifyPassword，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public static boolean verifyPassword(String rawPassword, String salt, String expectedHash) {
        String actualHash = hashPassword(rawPassword, salt);
        return MessageDigest.isEqual(
                actualHash.getBytes(StandardCharsets.UTF_8),
                expectedHash.getBytes(StandardCharsets.UTF_8)
        );
    }
}
