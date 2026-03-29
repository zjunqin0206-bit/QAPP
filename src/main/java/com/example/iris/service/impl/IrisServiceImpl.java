package com.example.iris.service.impl;

import com.example.iris.dto.IrisFilterRequest;
import com.example.iris.dto.IrisRequest;
import com.example.iris.entity.Iris;
import com.example.iris.enums.SpeciesType;
import com.example.iris.mapper.IrisMapper;
import com.example.iris.service.IrisService;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
/**
 * 文件说明：IrisServiceImpl 文件，承载该模块的核心职责与对外行为。
 * 函数概览：IrisServiceImpl、listAll、filter、getById、add、update。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class IrisServiceImpl implements IrisService {

    private static final Logger log = LoggerFactory.getLogger(IrisServiceImpl.class);
    private static final String SPECIES_ERROR_MESSAGE = "品种只允许为：Iris-setosa、Iris-versicolor";

    private final IrisMapper irisMapper;

    /**
     * 函数作用：IrisServiceImpl，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public IrisServiceImpl(IrisMapper irisMapper) {
        this.irisMapper = irisMapper;
    }

    @Override
    /**
     * 函数作用：listAll，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public List<Iris> listAll() {
        log.info("开始查询全部鸢尾花数据");
        List<Iris> list = irisMapper.selectAll();
        log.info("查询完成，返回记录数：{}", list.size());
        return list;
    }

    @Override
    /**
     * 函数作用：filter，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public List<Iris> filter(IrisFilterRequest request) {
        log.info("开始按条件筛选鸢尾花数据，request={}", request);
        validateRange(request.getSepalLengthMin(), request.getSepalLengthMax(), "花萼长度区间不合法");
        validateRange(request.getSepalWidthMin(), request.getSepalWidthMax(), "花萼宽度区间不合法");
        validateRange(request.getPetalLengthMin(), request.getPetalLengthMax(), "花瓣长度区间不合法");
        validateRange(request.getPetalWidthMin(), request.getPetalWidthMax(), "花瓣宽度区间不合法");

        List<Iris> list = irisMapper.selectByFilter(request);
        log.info("筛选完成，返回记录数：{}", list.size());
        return list;
    }

    @Override
    /**
     * 函数作用：getById，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Iris getById(Long id) {
        log.info("根据 ID 查询鸢尾花数据，id={}", id);
        Iris iris = irisMapper.selectById(id);
        if (iris == null) {
            log.warn("未查询到目标数据，id={}", id);
            throw new IllegalArgumentException("目标数据不存在，id=" + id);
        }
        return iris;
    }

    @Override
    /**
     * 函数作用：add，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Iris add(IrisRequest request) {
        log.info("开始新增鸢尾花数据，species={}", request.getSpecies());
        validateSpecies(request.getSpecies());

        Iris iris = Iris.builder()
                .sepalLength(request.getSepalLength())
                .sepalWidth(request.getSepalWidth())
                .petalLength(request.getPetalLength())
                .petalWidth(request.getPetalWidth())
                .species(request.getSpecies())
                .build();

        int rows = irisMapper.insert(iris);
        if (rows <= 0 || iris.getId() == null) {
            log.error("新增失败，影响行数：{}", rows);
            throw new RuntimeException("新增失败，请稍后重试");
        }

        log.info("新增成功，id={}", iris.getId());
        return irisMapper.selectById(iris.getId());
    }

    @Override
    /**
     * 函数作用：update，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Iris update(Long id, IrisRequest request) {
        log.info("开始更新鸢尾花数据，id={}", id);
        Iris existed = irisMapper.selectById(id);
        if (existed == null) {
            log.warn("更新失败，目标数据不存在，id={}", id);
            throw new IllegalArgumentException("目标数据不存在，id=" + id);
        }

        validateSpecies(request.getSpecies());

        Iris iris = Iris.builder()
                .id(id)
                .sepalLength(request.getSepalLength())
                .sepalWidth(request.getSepalWidth())
                .petalLength(request.getPetalLength())
                .petalWidth(request.getPetalWidth())
                .species(request.getSpecies())
                .build();

        int rows = irisMapper.updateById(iris);
        if (rows <= 0) {
            log.error("更新失败，id={}, 影响行数：{}", id, rows);
            throw new RuntimeException("更新失败，请稍后重试");
        }

        log.info("更新成功，id={}", id);
        return irisMapper.selectById(id);
    }

    @Override
    /**
     * 函数作用：delete，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public void delete(Long id) {
        log.info("开始删除鸢尾花数据，id={}", id);
        Iris existed = irisMapper.selectById(id);
        if (existed == null) {
            log.warn("删除失败，目标数据不存在，id={}", id);
            throw new IllegalArgumentException("目标数据不存在，id=" + id);
        }

        int rows = irisMapper.deleteById(id);
        if (rows <= 0) {
            log.error("删除失败，id={}, 影响行数：{}", id, rows);
            throw new RuntimeException("删除失败，请稍后重试");
        }

        log.info("删除成功，id={}", id);
    }

    /**
     * 函数作用：validateSpecies，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    private void validateSpecies(String species) {
        if (!SpeciesType.contains(species)) {
            throw new IllegalArgumentException(SPECIES_ERROR_MESSAGE);
        }
    }

    /**
     * 函数作用：validateRange，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    private void validateRange(Double min, Double max, String message) {
        if (min != null && max != null && min > max) {
            throw new IllegalArgumentException(message);
        }
    }
}
