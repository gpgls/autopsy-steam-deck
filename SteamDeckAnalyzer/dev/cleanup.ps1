Get-ChildItem -Path .\..\ -Recurse `
| Where-Object { $_.Name -match '(\.pyc|\$py\.class)$' } `
| ForEach-Object { Remove-Item -Path $_.FullName }
