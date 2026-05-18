# Contributing to ThunderGuard

Keep Git simple, and do not work directly on `main`.

## Basic Rules

1. `main` ต้องใช้งานได้เสมอ
2. ห้าม commit ตรงเข้า `main`
3. ใช้ 1 branch ต่อ 1 งาน
4. เปิด pull request ก่อน merge
5. ใช้ squash merge
6. Commit บ่อย ๆ 

Branch names should be short:

```bash
<your-name>/<short-topic>
```

Examples:

- `kj/feature-1`
- `pew/feature-2`
- `kong/feature-3`

## Daily Workflow

```bash
# เริ่มจาก main ล่าสุด
git checkout main
git pull

# สร้าง branch ใหม่สำหรับงานของเรา
git checkout -b your-name/short-topic

# แก้ไฟล์ แล้วบันทึกเป็น commit
git add .
git commit -m "area: short description"

# ทำซ้ำเป็นระยะ อย่ารอจนงานก้อนใหญ่จบค่อย commit
git add .
git commit -m "area: next small change"

# ดึง main ล่าสุดมารวมก่อนเปิด PR
git fetch origin
git merge origin/main

# ส่ง branch ขึ้น GitHub แล้วเปิด PR
git push -u origin your-name/short-topic
```

คำอธิบายเพิ่มเติม:

- `git checkout main`: ย้ายกลับไปที่ branch หลัก
- `git pull`: ดึง code ล่าสุดจาก GitHub
- `git checkout -b ...`: สร้าง branch ใหม่และย้ายเข้าไปทำงานใน branch นั้น
- `git add ...`: เลือกไฟล์ที่ต้องการใส่ใน commit
- `git commit -m ...`: บันทึกงานพร้อมข้อความสั้นๆ
- Commit บ่อย ๆ: แบ่งงานเป็นก้อนเล็ก ๆ เช่น แก้ parser, เพิ่ม dataset,
  ปรับ README แยกกัน เพื่อให้ review และ rollback ง่าย
- `git fetch origin`: เช็คว่าบน GitHub มี update ใหม่ไหม
- `git merge origin/main`: เอา update ล่าสุดจาก `main` มารวมกับ branch ของเรา
- `git push -u origin ...`: ส่ง branch ของเราขึ้น GitHub เพื่อเปิด PR

## Commit Messages

Use this format:

```text
area: what changed
```

Examples:

- `evaluate: pair XSTest with every attack dataset`
- `memory: add eviction policy`
- `attacks/zulu: generate prompts from AdvBench seeds`
- `docs: add IMAG paper notes`

Keep messages short. Simple is fine.

## Pull Request Template

```markdown
## What changed
- ...

## How to test
python scripts/run_eval.py --config configs/experiments/e3.yaml

## Results
- ...

## Links
- ...
```

## Do Not Commit

Never commit secrets or large local files.

Do not commit:

- `.env`
- API keys or tokens
- model files like `*.pt`, `*.bin`, `*.safetensors`, `*.gguf`, `*.ckpt`
- virtual environments like `.venv/`, `venv/`, `env/`
- cache folders

## Common Problems

### เผลอ commit บน `main`

ใช้คำสั่งนี้เพื่อย้ายงานออกจาก `main` ไปไว้ใน branch ใหม่:

```bash
git reset HEAD~1
git stash
git checkout -b your-name/short-topic
git stash pop
git add .
git commit -m "area: short description"
git push -u origin your-name/short-topic
```

คำอธิบาย:

- `git reset HEAD~1`: ยกเลิก commit ล่าสุด แต่ไฟล์ที่แก้ยังอยู่
- `git stash`: เก็บงานที่แก้ไว้ชั่วคราว
- `git checkout -b ...`: สร้าง branch ใหม่
- `git stash pop`: เอางานที่เก็บไว้กลับมา
- จากนั้น `add`, `commit`, และ `push` ตามปกติ

### เจอ merge conflict

ดึง `main` ล่าสุดมารวมกับ branch ของเรา:

```bash
git fetch origin
git merge origin/main
```

Git จะบอกว่าไฟล์ไหนมีปัญหา ให้เปิดไฟล์นั้น แล้วลบเครื่องหมาย conflict ออก:

```text
<<<<<<<
=======
>>>>>>>
```

เลือก code ที่ถูกต้องไว้ แล้ว run:

```bash
git add <file>
git commit
```

### commit หาย หรือหา code ไม่เจอ

ใช้ `git reflog` เพื่อดูประวัติการย้าย branch และ commit:

```bash
git reflog
git checkout <sha>
git checkout -b recovery
```

คำอธิบาย:

- `git reflog`: ดูประวัติว่า HEAD เคยอยู่ที่ commit ไหนบ้าง
- `git checkout <sha>`: ย้ายไปดู commit ที่ต้องการกู้คืน
- `git checkout -b recovery`: สร้าง branch ใหม่จาก commit นั้น

### เผลอ push ของที่ไม่ควร push

โดยเฉพาะถ้าเป็น secret หรือไฟล์ใหญ่มาก

ถ้าอยู่แค่ใน branch ของตัวเอง อาจต้องใช้:

```bash
git push --force-with-lease
```

ห้าม force-push ไปที่ `main`
