package com.example.iris.controller;

import com.example.iris.common.Result;
import com.example.iris.dto.IrisFilterRequest;
import com.example.iris.dto.IrisRequest;
import com.example.iris.entity.Iris;
import com.example.iris.service.IrisService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/iris")
/**
 * 文件说明：IrisController 文件，承载该模块的核心职责与对外行为。
 * 函数概览：IrisController、list、add。
 * 实现思路：按功能段组织流程，围绕参数校验、业务规则与数据读写边界展开。
 */
public class IrisController {

    private static final Logger log = LoggerFactory.getLogger(IrisController.class);

    private final IrisService irisService;

    /**
     * 函数作用：IrisController，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public IrisController(IrisService irisService) {
        this.irisService = irisService;
    }

    @GetMapping("/list")
    /**
     * 函数作用：list，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<List<Iris>> list() {
        log.info("接收到查询全部鸢尾花数据请求");
        return Result.success(irisService.listAll());
    }

    @PostMapping("/filter")
    public Result<List<Iris>> filter(@RequestBody(required = false) IrisFilterRequest request) {
        IrisFilterRequest actualRequest = request == null ? new IrisFilterRequest() : request;
        log.info("接收到条件筛选请求，request={}", actualRequest);
        return Result.success(irisService.filter(actualRequest));
    }

    @GetMapping("/get/{id}")
    public Result<Iris> getById(@PathVariable @Min(value = 1, message = "id 必须大于等于 1") Long id) {
        log.info("接收到根据 ID 查询请求，id={}", id);
        return Result.success(irisService.getById(id));
    }

    @PostMapping("/add")
    /**
     * 函数作用：add，承担当前功能段的核心处理步骤。
     * 实现思路：先做输入与上下文准备，再执行业务与数据操作，最后统一返回结果或抛出异常。
     */
    public Result<Iris> add(@Valid @RequestBody IrisRequest request) {
        log.info("接收到新增鸢尾花数据请求，species={}", request.getSpecies());
        return Result.success(irisService.add(request));
    }

    @PutMapping("/update/{id}")
    public Result<Iris> update(@PathVariable @Min(value = 1, message = "id 必须大于等于 1") Long id,
                               @Valid @RequestBody IrisRequest request) {
        log.info("接收到更新鸢尾花数据请求，id={}", id);
        return Result.success(irisService.update(id, request));
    }

    @DeleteMapping("/delete/{id}")
    public Result<String> delete(@PathVariable @Min(value = 1, message = "id 必须大于等于 1") Long id) {
        log.info("接收到删除鸢尾花数据请求，id={}", id);
        irisService.delete(id);
        return Result.success("删除成功");
    }
}
