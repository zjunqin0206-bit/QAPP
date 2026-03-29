package com.example.iris;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.example.iris.mapper")
/**
 * 文件说明：IrisApplication 文件，承载该模块的核心职责与对外行为。
 * 函数概览：main。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class IrisApplication {

    /**
     * 函数作用：main，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public static void main(String[] args) {
        SpringApplication.run(IrisApplication.class, args);
    }
}
