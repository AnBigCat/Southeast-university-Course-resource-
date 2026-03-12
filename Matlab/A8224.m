s=rand;
s1=fix(rem(s,100));
s2=input('请输入猜测');
for i=1:7
if s2>s1
    disp('high')
    s2=input('请再输入猜测');
elseif s2<s1
      disp('low')
      s2=input('请再输入猜测');
elseif s1==s2
     disp('you won!')
     break
end
end


            
     