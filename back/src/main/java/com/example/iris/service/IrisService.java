package com.example.iris.service;

import com.example.iris.dto.IrisFilterRequest;
import com.example.iris.dto.IrisRequest;
import com.example.iris.entity.Iris;
import java.util.List;

/**
 * 文件说明：IrisService 文件，承载该模块的核心职责与对外行为。
 * 函数概览：见各方法注释。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public interface IrisService {

    List<Iris> listAll();

    List<Iris> filter(IrisFilterRequest request);

    Iris getById(Long id);

    Iris add(IrisRequest request);

    Iris update(Long id, IrisRequest request);

    void delete(Long id);
}
