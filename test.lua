function factorial(n)
    if n == 0 then
        return 1
    else
        return n * factorial(n - 1)
    end
end

local a
a = 5

local n = 100000

print(factorial(a)) -- 120
print(factorial(0)) -- 1
print(n)