function fibo = fibonacci(n)
    % 递归函数计算斐波那契数列的第n项
    if n <= 0
        error('n must be a positive integer');
    elseif n == 1 || n == 2
        fibo = 1;  % 斐波那契数列的前两项都是1
    else
        fibo = fibonacci(n-1) + fibonacci(n-2);  % 递归调用
    end
end

% 主程序
n = 20;
fibo_n = fibonacci(n);
disp(['The 20th Fibonacci number is: ', num2str(fibo_n)]);