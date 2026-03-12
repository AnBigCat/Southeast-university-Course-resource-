for i=100:999
    a=fix(i/100);
    b=fix((i-fix(i/100).*100)/10);
    c=(i-fix(i/10).*10);
    if i==a^3+b^3+c^3
        disp(i);
    end
end

