#!/bin/bash
echo "🚀 部署 N.S.S Novena Garfield"
echo "目标: N_S_S_Novena_Garfield.surge.sh"

# 安装surge (如果未安装)
if ! command -v surge &> /dev/null; then
    npm install -g surge
fi

# 部署
surge nss-redirect.html N_S_S_Novena_Garfield.surge.sh

echo "✅ 部署完成！"
echo "🌐 访问: https://N_S_S_Novena_Garfield.surge.sh"
