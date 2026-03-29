package com.example.iris.mapper;

import com.example.iris.dto.IrisFilterRequest;
import com.example.iris.entity.Iris;
import java.util.List;

/**
 * 文件说明：IrisMapper 文件，承载该模块的核心职责与对外行为。
 * 函数概览：见各方法注释。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public interface IrisMapper {

    List<Iris> selectAll();

    List<Iris> selectByFilter(IrisFilterRequest request);

    Iris selectById(Long id);

    int insert(Iris iris);

    int updateById(Iris iris);

    int deleteById(Long id);
}
