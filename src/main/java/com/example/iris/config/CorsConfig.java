package com.example.iris.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
/**
 * 文件说明：CorsConfig 文件，承载该模块的核心职责与对外行为。
 * 函数概览：addCorsMappings。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class CorsConfig implements WebMvcConfigurer {

    @Override
    /**
     * 函数作用：addCorsMappings，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOriginPatterns("*")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }
}
