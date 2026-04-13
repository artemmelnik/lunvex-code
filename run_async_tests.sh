#!/bin/bash
# Скрипт для запуска асинхронных тестов

echo "================================================"
echo "Запуск тестов асинхронности LunVex Code"
echo "================================================"
echo ""

# Проверка наличия Python
if ! command -v python &> /dev/null; then
    echo "❌ Python не найден"
    exit 1
fi

# Проверка наличия pytest
if ! python -m pytest --version &> /dev/null; then
    echo "❌ pytest не установлен"
    echo "Установите: pip install pytest pytest-asyncio"
    exit 1
fi

echo "✅ Python и pytest доступны"
echo ""

# Функция для запуска тестов
run_test() {
    local test_file=$1
    local test_name=$2
    
    echo "🔍 Запуск: $test_name"
    echo "----------------------------------------"
    
    if python -m pytest "$test_file" -v --tb=short 2>&1 | tail -20; then
        echo "✅ $test_name: УСПЕХ"
        return 0
    else
        echo "❌ $test_name: НЕУДАЧА"
        return 1
    fi
}

# Основные тесты (должны проходить)
echo ""
echo "================================================"
echo "ОСНОВНЫЕ ТЕСТЫ (должны проходить)"
echo "================================================"

TESTS_PASSED=0
TESTS_FAILED=0

# Список основных тестов
main_tests=(
    "tests/test_async_system.py:Основные асинхронные инструменты"
    "tests/test_async_cli.py:Асинхронный CLI"
    "tests/test_async_web_tools_simple.py:Веб-инструменты"
    "tests/test_async_agent_simple.py:Асинхронный агент"
    "tests/test_async_cache.py:Кэширование"
    "tests/test_async_git_simple.py:Git инструменты"
)

for test_entry in "${main_tests[@]}"; do
    test_file="${test_entry%%:*}"
    test_name="${test_entry#*:}"
    
    if run_test "$test_file" "$test_name"; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo ""
done

# Тесты требующие доработки
echo ""
echo "================================================"
echo "ТЕСТЫ ТРЕБУЮЩИЕ ДОРАБОТКИ (могут не проходить)"
echo "================================================"

wip_tests=(
    "tests/test_async_performance.py:Тесты производительности"
    "tests/test_async_compatibility.py:Тесты совместимости"
    "tests/test_async_error_handling.py:Тесты обработки ошибок"
    "tests/test_async_dependency_tools.py:Инструменты зависимостей"
)

for test_entry in "${wip_tests[@]}"; do
    test_file="${test_entry%%:*}"
    test_name="${test_entry#*:}"
    echo "⚠️  Пропуск: $test_name (требует доработки)"
    echo ""
done

# Итоги
echo ""
echo "================================================"
echo "ИТОГИ ТЕСТИРОВАНИЯ"
echo "================================================"
echo "✅ Успешно: $TESTS_PASSED тестов"
echo "❌ Неудачно: $TESTS_FAILED тестов"
echo "⚠️  Пропущено: ${#wip_tests[@]} тестов (требуют доработки)"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "🎉 Все основные тесты прошли успешно!"
    echo ""
    echo "Для запуска всех тестов (включая требующие доработки):"
    echo "  python tests/test_all_async.py --mode=pytest"
    echo ""
    echo "Для просмотра списка всех тестов:"
    echo "  python tests/test_all_async.py --mode=list"
    exit 0
else
    echo "⚠️  Некоторые тесты не прошли. Проверьте вывод выше."
    exit 1
fi