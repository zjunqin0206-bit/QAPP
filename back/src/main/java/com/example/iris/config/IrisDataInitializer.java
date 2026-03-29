package com.example.iris.config;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
/**
 * 文件说明：IrisDataInitializer 文件，负责 iris 表结构检查与基础数据初始化。
 * 函数概览：IrisDataInitializer、run、ensureIrisTable、seedIrisDataIfEmpty。
 * 实现思路：先保证数据表存在，再以“空表才灌入”的策略初始化样例数据，避免覆盖线上数据。
 */
public class IrisDataInitializer implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(IrisDataInitializer.class);

    private final DataSource dataSource;

    /**
     * 函数作用：IrisDataInitializer，注入数据源用于后续建表与初始化操作。
     * 实现思路：构造阶段仅保存依赖，不做数据库副作用操作，避免容器启动链路耦合。
     */
    public IrisDataInitializer(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    /**
     * 函数作用：run，应用启动后执行 iris 表检查与初始数据注入。
     * 实现思路：按“建表 -> 检查数据量 -> 按需灌入”顺序执行，确保初始化过程幂等。
     */
    public void run(ApplicationArguments args) {
        ensureIrisTable();
        seedIrisDataIfEmpty();
    }

    /**
     * 函数作用：ensureIrisTable，确保 iris 表存在且字段满足当前后端映射。
     * 实现思路：使用 DDL 兜底创建表结构，字段名与 MyBatis 映射保持一致。
     */
    private void ensureIrisTable() {
        String sql = "CREATE TABLE IF NOT EXISTS iris (\n"
                + "  id BIGINT PRIMARY KEY AUTO_INCREMENT,\n"
                + "  sepal_length DOUBLE NOT NULL,\n"
                + "  sepal_width DOUBLE NOT NULL,\n"
                + "  petal_length DOUBLE NOT NULL,\n"
                + "  petal_width DOUBLE NOT NULL,\n"
                + "  `class` VARCHAR(50) NOT NULL\n"
                + ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;";
        try (Connection connection = dataSource.getConnection(); Statement statement = connection.createStatement()) {
            statement.execute(sql);
        } catch (Exception ex) {
            log.error("创建 iris 表失败", ex);
            throw new RuntimeException("数据库初始化失败：iris 表创建失败", ex);
        }
    }

    /**
     * 函数作用：seedIrisDataIfEmpty，仅在空表时写入 iris 基础样例数据。
     * 实现思路：先查询总数，若已有数据直接返回；若为空则批量插入三类样例记录。
     */
    private void seedIrisDataIfEmpty() {
        String countSql = "SELECT COUNT(*) FROM iris";
        String insertSql = "INSERT INTO iris (sepal_length, sepal_width, petal_length, petal_width, `class`) VALUES (?, ?, ?, ?, ?)";

        Object[][] seeds = new Object[][]{
                {5.1, 3.5, 1.4, 0.2, "Iris-setosa"},
                {4.9, 3.0, 1.4, 0.2, "Iris-setosa"},
                {5.4, 3.9, 1.7, 0.4, "Iris-setosa"},
                {7.0, 3.2, 4.7, 1.4, "Iris-versicolor"},
                {6.4, 3.2, 4.5, 1.5, "Iris-versicolor"},
                {6.9, 3.1, 4.9, 1.5, "Iris-versicolor"},
                {6.3, 3.3, 6.0, 2.5, "Iris-virginica"},
                {5.8, 2.7, 5.1, 1.9, "Iris-virginica"},
                {7.1, 3.0, 5.9, 2.1, "Iris-virginica"}
        };

        try (Connection connection = dataSource.getConnection();
             Statement countStatement = connection.createStatement();
             ResultSet resultSet = countStatement.executeQuery(countSql)) {

            long count = 0;
            if (resultSet.next()) {
                count = resultSet.getLong(1);
            }

            if (count > 0) {
                log.info("iris 表已存在数据，跳过初始化，当前记录数={}", count);
                return;
            }

            try (PreparedStatement preparedStatement = connection.prepareStatement(insertSql)) {
                for (Object[] row : seeds) {
                    preparedStatement.setDouble(1, (Double) row[0]);
                    preparedStatement.setDouble(2, (Double) row[1]);
                    preparedStatement.setDouble(3, (Double) row[2]);
                    preparedStatement.setDouble(4, (Double) row[3]);
                    preparedStatement.setString(5, (String) row[4]);
                    preparedStatement.addBatch();
                }
                preparedStatement.executeBatch();
            }

            log.info("iris 表为空，已初始化 {} 条样例数据", seeds.length);
        } catch (Exception ex) {
            log.error("初始化 iris 样例数据失败", ex);
            throw new RuntimeException("数据库初始化失败：iris 样例数据写入失败", ex);
        }
    }
}
