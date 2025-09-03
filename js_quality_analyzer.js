#!/usr/bin/env node
/**
 * JavaScript测试质量评估脚本
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class JSQualityAnalyzer {
    constructor(projectRoot = '.') {
        this.projectRoot = projectRoot;
        this.qualityScores = {};
        this.issues = {};
    }

    checkToolsAvailability() {
        console.log('🔍 检查JavaScript质量评估工具...');
        
        const tools = {
            'eslint': 'eslint --version',
            'jest': 'jest --version'
        };
        
        const availableTools = {};
        
        for (const [toolName, command] of Object.entries(tools)) {
            try {
                const result = execSync(command, { encoding: 'utf8' });
                availableTools[toolName] = true;
                console.log(`✅ ${toolName}: 可用 (${result.trim()})`);
            } catch (error) {
                availableTools[toolName] = false;
                console.log(`❌ ${toolName}: 不可用`);
            }
        }
        
        return availableTools;
    }

    analyzeCodeComplexity(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            let complexity = 1;
            
            const patterns = [
                /if\s*\(/g,
                /for\s*\(/g,
                /while\s*\(/g,
                /switch\s*\(/g,
                /case\s+/g,
                /catch\s*\(/g,
                /\|\||&&/g
            ];
            
            patterns.forEach(pattern => {
                const matches = content.match(pattern);
                if (matches) {
                    complexity += matches.length;
                }
            });
            
            return complexity;
        } catch (error) {
            return 1;
        }
    }

    analyzeTestCoverageStatic(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            let testFunctions = 0;
            let totalFunctions = 0;
            
            const functionPatterns = [
                /function\s+\w+\s*\(/g,
                /const\s+\w+\s*=\s*\([^)]*\)\s*=>/g,
                /let\s+\w+\s*=\s*\([^)]*\)\s*=>/g
            ];
            
            functionPatterns.forEach(pattern => {
                const matches = content.match(pattern);
                if (matches) {
                    totalFunctions += matches.length;
                }
            });
            
            const testPatterns = [
                /describe\s*\(/g,
                /it\s*\(/g,
                /test\s*\(/g
            ];
            
            testPatterns.forEach(pattern => {
                const matches = content.match(pattern);
                if (matches) {
                    testFunctions += matches.length;
                }
            });
            
            const coverage = totalFunctions > 0 ? (testFunctions / totalFunctions * 100) : 0;
            
            return {
                testFunctions,
                totalFunctions,
                coveragePercentage: coverage
            };
        } catch (error) {
            return { testFunctions: 0, totalFunctions: 0, coveragePercentage: 0 };
        }
    }

    analyzeCodingStandards(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const issues = [];
            const lines = content.split('\n');
            
            const longLines = lines
                .map((line, index) => ({ line: line.trim(), lineNumber: index + 1 }))
                .filter(({ line }) => line.length > 120);
            
            if (longLines.length > 0) {
                issues.push(`超长行: ${longLines.length}行`);
            }
            
            let consecutiveEmpty = 0;
            for (const line of lines) {
                if (line.trim() === '') {
                    consecutiveEmpty++;
                } else {
                    consecutiveEmpty = 0;
                }
                if (consecutiveEmpty > 2) {
                    issues.push('连续空行过多');
                    break;
                }
            }
            
            return issues;
        } catch (error) {
            return ['分析失败'];
        }
    }

    runESLintAnalysis(filePath, availableTools) {
        if (!availableTools.eslint) {
            return { score: 0.0, issues: ['ESLint不可用'] };
        }
        
        try {
            const result = execSync(`eslint --format=json "${filePath}"`, { 
                encoding: 'utf8',
                stdio: ['pipe', 'pipe', 'pipe']
            });
            
            try {
                const eslintOutput = JSON.parse(result);
                if (eslintOutput.length > 0) {
                    const fileIssues = eslintOutput[0].messages;
                    const issues = fileIssues.map(msg => `${msg.line}:${msg.column} ${msg.message}`);
                    
                    const errors = fileIssues.filter(msg => msg.severity === 2).length;
                    const warnings = fileIssues.filter(msg => msg.severity === 1).length;
                    const score = Math.max(0, 10 - errors * 2 - warnings * 0.5);
                    
                    return { score, issues };
                } else {
                    return { score: 10.0, issues: [] };
                }
            } catch (parseError) {
                return { score: 0.0, issues: ['ESLint输出解析失败'] };
            }
        } catch (error) {
            return { score: 10.0, issues: [] };
        }
    }

    analyzeFileQuality(filePath, availableTools) {
        console.log(`🔍 分析文件: ${filePath}`);
        
        const fileQuality = {
            filePath: filePath,
            complexity: this.analyzeCodeComplexity(filePath),
            testCoverage: this.analyzeTestCoverageStatic(filePath),
            codingStandards: this.analyzeCodingStandards(filePath),
            eslintScore: 0.0
        };
        
        const eslintResult = this.runESLintAnalysis(filePath, availableTools);
        fileQuality.eslintScore = eslintResult.score;
        if (eslintResult.issues.length > 0) {
            this.issues[filePath] = eslintResult.issues;
        }
        
        const qualityScore = this.calculateQualityScore(fileQuality);
        fileQuality.qualityScore = qualityScore;
        
        return fileQuality;
    }

    calculateQualityScore(fileQuality) {
        let score = 100;
        
        const complexity = fileQuality.complexity;
        if (complexity > 10) {
            score -= (complexity - 10) * 2;
        } else if (complexity > 5) {
            score -= (complexity - 5);
        }
        
        const coverage = fileQuality.testCoverage.coveragePercentage;
        if (coverage < 80) {
            score -= (80 - coverage) * 0.5;
        }
        
        const eslintScore = fileQuality.eslintScore;
        if (eslintScore < 8.0) {
            score -= (8.0 - eslintScore) * 2;
        }
        
        const standardsIssues = fileQuality.codingStandards.length;
        score -= standardsIssues * 2;
        
        return Math.max(0, score);
    }

    async analyzeAllTestFiles() {
        console.log('🚀 开始JavaScript测试文件质量分析...');
        
        const availableTools = this.checkToolsAvailability();
        
        let testReport;
        try {
            const reportContent = fs.readFileSync('test_structure_report.json', 'utf8');
            testReport = JSON.parse(reportContent);
        } catch (error) {
            console.log('❌ 找不到test_structure_report.json');
            return;
        }
        
        const jsTestFiles = [];
        for (const [dirName, files] of Object.entries(testReport.directory_structure)) {
            for (const fileInfo of files) {
                if (fileInfo.type === 'javascript') {
                    const filePath = path.join(fileInfo.file);
                    if (fs.existsSync(filePath)) {
                        jsTestFiles.push(filePath);
                    }
                }
            }
        }
        
        console.log(`📁 找到 ${jsTestFiles.length} 个JavaScript测试文件`);
        
        for (const filePath of jsTestFiles) {
            try {
                const fileQuality = this.analyzeFileQuality(filePath, availableTools);
                this.qualityScores[filePath] = fileQuality;
            } catch (error) {
                console.log(`❌ 分析文件失败 ${filePath}: ${error.message}`);
            }
        }
        
        this.generateQualityReport(availableTools);
        
        console.log('✅ JavaScript质量分析完成！');
    }

    generateQualityReport(availableTools) {
        console.log('📊 生成JavaScript质量分析报告...');
        
        const totalFiles = Object.keys(this.qualityScores).length;
        if (totalFiles === 0) {
            console.log('❌ 没有可分析的文件');
            return;
        }
        
        const avgQualityScore = Object.values(this.qualityScores)
            .reduce((sum, f) => sum + f.qualityScore, 0) / totalFiles;
        
        const avgComplexity = Object.values(this.qualityScores)
            .reduce((sum, f) => sum + f.complexity, 0) / totalFiles;
        
        const avgCoverage = Object.values(this.qualityScores)
            .reduce((sum, f) => sum + f.testCoverage.coveragePercentage, 0) / totalFiles;
        
        const qualityDistribution = {
            excellent: Object.values(this.qualityScores).filter(f => f.qualityScore >= 90).length,
            good: Object.values(this.qualityScores).filter(f => f.qualityScore >= 80 && f.qualityScore < 90).length,
            fair: Object.values(this.qualityScores).filter(f => f.qualityScore >= 70 && f.qualityScore < 80).length,
            poor: Object.values(this.qualityScores).filter(f => f.qualityScore < 70).length
        };
        
        const report = {
            summary: {
                totalFiles,
                averageQualityScore: Math.round(avgQualityScore * 100) / 100,
                averageComplexity: Math.round(avgComplexity * 100) / 100,
                averageTestCoverage: Math.round(avgCoverage * 100) / 100,
                availableTools
            },
            qualityDistribution,
            fileQualityDetails: this.qualityScores,
            issuesSummary: this.issues
        };
        
        fs.writeFileSync('js_quality_analysis_report.json', JSON.stringify(report, null, 2), 'utf8');
        
        console.log('✅ JavaScript质量分析报告已生成: js_quality_analysis_report.json');
        
        console.log(`\n📈 JavaScript质量分析摘要:`);
        console.log(`   - 分析文件数: ${totalFiles}`);
        console.log(`   - 平均质量评分: ${avgQualityScore.toFixed(2)}/100`);
        console.log(`   - 平均复杂度: ${avgComplexity.toFixed(2)}`);
        console.log(`   - 平均测试覆盖率: ${avgCoverage.toFixed(2)}%`);
        console.log(`   - 优秀文件: ${qualityDistribution.excellent}`);
        console.log(`   - 良好文件: ${qualityDistribution.good}`);
        console.log(`   - 一般文件: ${qualityDistribution.fair}`);
        console.log(`   - 较差文件: ${qualityDistribution.poor}`);
    }
}

async function main() {
    const analyzer = new JSQualityAnalyzer();
    await analyzer.analyzeAllTestFiles();
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = JSQualityAnalyzer;
