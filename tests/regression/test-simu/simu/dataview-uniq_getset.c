#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include "dataview-uniq_getset.h"

size_t GetStreamCurrentLength(BitStream *pBitStrm) {
    return pBitStrm->currentByte + ((pBitStrm->currentBit+7)/8);
}

byte *GetBitstreamBuffer(BitStream *pBitStrm) {
    return pBitStrm->buf;
}

byte GetBufferByte(byte *p, size_t off) {
    assert(p);
    return p[off];
}

void SetBufferByte(byte *p, size_t off, byte b) {
    assert(p);
    p[off] = b;
}

void ResetStream(BitStream *pStrm) {
    assert(pStrm);
    assert(pStrm->count > 0);
    pStrm->currentByte = 0;
    pStrm->currentBit = 0;
}

BitStream *CreateStream(size_t bufferSize) {
    BitStream *pBitStrm = malloc(sizeof(BitStream));
    assert(pBitStrm);
    pBitStrm->buf = malloc(bufferSize);
    assert(pBitStrm->buf);
    pBitStrm->count = bufferSize;
    memset(pBitStrm->buf, 0x0, bufferSize);
    ResetStream(pBitStrm);
    return pBitStrm;
}

void DestroyStream(BitStream *pBitStrm) {
    assert(pBitStrm);
    assert(pBitStrm->buf);
    free(pBitStrm->buf);
    free(pBitStrm);
}


/* INTEGER */
asn1SccSint T_UInt32__Get(T_UInt32* root)
{
    return (*root);
}

/* INTEGER */
void T_UInt32__Set(T_UInt32* root, asn1SccSint value)
{
    (*root) = value;
}

/* INTEGER */
asn1SccSint TASTE_Peek_id__Get(TASTE_Peek_id* root)
{
    return (*root);
}

/* INTEGER */
void TASTE_Peek_id__Set(TASTE_Peek_id* root, asn1SccSint value)
{
    (*root) = value;
}

/* SEQUENCEOF/SETOF */
long TASTE_Peek_id_list__GetLength(TASTE_Peek_id_list* root)
{
    return (*root).nCount;
}

/* SEQUENCEOF/SETOF */
void TASTE_Peek_id_list__SetLength(TASTE_Peek_id_list* root, long value)
{
    (*root).nCount = value;
}

/* INTEGER */
asn1SccSint TASTE_Peek_id_list__iDx_Get(TASTE_Peek_id_list* root, int iDx)
{
    return (*root).arr[iDx];
}

/* INTEGER */
void TASTE_Peek_id_list__iDx_Set(TASTE_Peek_id_list* root, int iDx, asn1SccSint value)
{
    (*root).arr[iDx] = value;
}

/* SEQUENCEOF/SETOF */
long MySetOf__GetLength(MySetOf* root)
{
    return (*root).nCount;
}

/* SEQUENCEOF/SETOF */
void MySetOf__SetLength(MySetOf* root, long value)
{
    (*root).nCount = value;
}

/* INTEGER */
asn1SccSint MySetOf__iDx_Get(MySetOf* root, int iDx)
{
    return (*root).arr[iDx];
}

/* INTEGER */
void MySetOf__iDx_Set(MySetOf* root, int iDx, asn1SccSint value)
{
    (*root).arr[iDx] = value;
}

/* INTEGER */
asn1SccSint MySimpleSeq__a_Get(MySimpleSeq* root)
{
    return (*root).a;
}

/* INTEGER */
void MySimpleSeq__a_Set(MySimpleSeq* root, asn1SccSint value)
{
    (*root).a = value;
}

/* BOOLEAN */
flag MySimpleSeq__b_Get(MySimpleSeq* root)
{
    return (*root).b;
}

/* BOOLEAN */
void MySimpleSeq__b_Set(MySimpleSeq* root, flag value)
{
    (*root).b = value;
}

/* ENUMERATED */
int MySimpleSeq__c_Get(MySimpleSeq* root)
{
    return (*root).c;
}

/* ENUMERATED */
void MySimpleSeq__c_Set(MySimpleSeq* root, int value)
{
    (*root).c = value;
}

/* SEQUENCEOF/SETOF */
long FixedIntList__GetLength(FixedIntList* root)
{
    return 3;
}

/* SEQUENCEOF/SETOF */
void FixedIntList__SetLength(FixedIntList* root, long value)
{
    fprintf(stderr, "WARNING: setting length of fixed-length sequence\n");
}

/* INTEGER */
asn1SccSint FixedIntList__iDx_Get(FixedIntList* root, int iDx)
{
    return (*root).arr[iDx];
}

/* INTEGER */
void FixedIntList__iDx_Set(FixedIntList* root, int iDx, asn1SccSint value)
{
    (*root).arr[iDx] = value;
}

/* BOOLEAN */
flag MySeq__a_Get(MySeq* root)
{
    return (*root).a;
}

/* BOOLEAN */
void MySeq__a_Set(MySeq* root, flag value)
{
    (*root).a = value;
}

/* Field b selector */
MyChoice* MySeq__b_Get(MySeq* root)
{
    return &(*root).b;
}

/* CHOICE selector */
int MySeq__b_kind_Get(MySeq* root)
{
    return (*root).b.kind;
}

/* CHOICE selector */
void MySeq__b_kind_Set(MySeq* root, int value)
{
    (*root).b.kind = value;
}

/* BOOLEAN */
flag MySeq__b_a_Get(MySeq* root)
{
    return (*root).b.u.a;
}

/* BOOLEAN */
void MySeq__b_a_Set(MySeq* root, flag value)
{
    (*root).b.u.a = value;
}

/* ENUMERATED */
int MySeq__b_b_Get(MySeq* root)
{
    return (*root).b.u.b;
}

/* ENUMERATED */
void MySeq__b_b_Set(MySeq* root, int value)
{
    (*root).b.u.b = value;
}

/* CHOICE selector */
int MyChoice__kind_Get(MyChoice* root)
{
    return (*root).kind;
}

/* CHOICE selector */
void MyChoice__kind_Set(MyChoice* root, int value)
{
    (*root).kind = value;
}

/* BOOLEAN */
flag MyChoice__a_Get(MyChoice* root)
{
    return (*root).u.a;
}

/* BOOLEAN */
void MyChoice__a_Set(MyChoice* root, flag value)
{
    (*root).u.a = value;
}

/* ENUMERATED */
int MyChoice__b_Get(MyChoice* root)
{
    return (*root).u.b;
}

/* ENUMERATED */
void MyChoice__b_Set(MyChoice* root, int value)
{
    (*root).u.b = value;
}

/* ENUMERATED */
int MyEnum__Get(MyEnum* root)
{
    return (*root);
}

/* ENUMERATED */
void MyEnum__Set(MyEnum* root, int value)
{
    (*root) = value;
}

/* SEQUENCEOF/SETOF */
long MySeqOf__GetLength(MySeqOf* root)
{
    return (*root).nCount;
}

/* SEQUENCEOF/SETOF */
void MySeqOf__SetLength(MySeqOf* root, long value)
{
    (*root).nCount = value;
}

/* INTEGER */
asn1SccSint MySeqOf__iDx_Get(MySeqOf* root, int iDx)
{
    return (*root).arr[iDx];
}

/* INTEGER */
void MySeqOf__iDx_Set(MySeqOf* root, int iDx, asn1SccSint value)
{
    (*root).arr[iDx] = value;
}

/* Helper functions for NATIVE encodings */

void SetDataFor_T_UInt32(void *dest, void *src)
{
    memcpy(dest, src, sizeof(T_UInt32));
}

byte* MovePtrBySizeOf_T_UInt32(byte *pData)
{
    return pData + sizeof(T_UInt32);
}

byte* CreateInstanceOf_T_UInt32() {
    T_UInt32 *p = (T_UInt32*)malloc(sizeof(T_UInt32));
    T_UInt32_Initialize(p);
    return (byte*)p;
}

void DestroyInstanceOf_T_UInt32(byte *pData) {
    free(pData);
}

void SetDataFor_TASTE_Peek_id(void *dest, void *src)
{
    memcpy(dest, src, sizeof(TASTE_Peek_id));
}

byte* MovePtrBySizeOf_TASTE_Peek_id(byte *pData)
{
    return pData + sizeof(TASTE_Peek_id);
}

byte* CreateInstanceOf_TASTE_Peek_id() {
    TASTE_Peek_id *p = (TASTE_Peek_id*)malloc(sizeof(TASTE_Peek_id));
    TASTE_Peek_id_Initialize(p);
    return (byte*)p;
}

void DestroyInstanceOf_TASTE_Peek_id(byte *pData) {
    free(pData);
}

void SetDataFor_TASTE_Peek_id_list(void *dest, void *src)
{
    memcpy(dest, src, sizeof(TASTE_Peek_id_list));
}

byte* MovePtrBySizeOf_TASTE_Peek_id_list(byte *pData)
{
    return pData + sizeof(TASTE_Peek_id_list);
}

byte* CreateInstanceOf_TASTE_Peek_id_list() {
    TASTE_Peek_id_list *p = (TASTE_Peek_id_list*)malloc(sizeof(TASTE_Peek_id_list));
    TASTE_Peek_id_list_Initialize(p);
    return (byte*)p;
}

void DestroyInstanceOf_TASTE_Peek_id_list(byte *pData) {
    free(pData);
}

void SetDataFor_MySetOf(void *dest, void *src)
{
    memcpy(dest, src, sizeof(MySetOf));
}

byte* MovePtrBySizeOf_MySetOf(byte *pData)
{
    return pData + sizeof(MySetOf);
}

byte* CreateInstanceOf_MySetOf() {
    MySetOf *p = (MySetOf*)malloc(sizeof(MySetOf));
    MySetOf_Initialize(p);
    return (byte*)p;
}

void DestroyInstanceOf_MySetOf(byte *pData) {
    free(pData);
}

void SetDataFor_MySimpleSeq(void *dest, void *src)
{
    memcpy(dest, src, sizeof(MySimpleSeq));
}

byte* MovePtrBySizeOf_MySimpleSeq(byte *pData)
{
    return pData + sizeof(MySimpleSeq);
}

byte* CreateInstanceOf_MySimpleSeq() {
    MySimpleSeq *p = (MySimpleSeq*)malloc(sizeof(MySimpleSeq));
    MySimpleSeq_Initialize(p);
    return (byte*)p;
}

void DestroyInstanceOf_MySimpleSeq(byte *pData) {
    free(pData);
}

void SetDataFor_FixedIntList(void *dest, void *src)
{
    memcpy(dest, src, sizeof(FixedIntList));
}

byte* MovePtrBySizeOf_FixedIntList(byte *pData)
{
    return pData + sizeof(FixedIntList);
}

byte* CreateInstanceOf_FixedIntList() {
    FixedIntList *p = (FixedIntList*)malloc(sizeof(FixedIntList));
    FixedIntList_Initialize(p);
    return (byte*)p;
}

void DestroyInstanceOf_FixedIntList(byte *pData) {
    free(pData);
}

void SetDataFor_MySeq(void *dest, void *src)
{
    memcpy(dest, src, sizeof(MySeq));
}

byte* MovePtrBySizeOf_MySeq(byte *pData)
{
    return pData + sizeof(MySeq);
}

byte* CreateInstanceOf_MySeq() {
    MySeq *p = (MySeq*)malloc(sizeof(MySeq));
    MySeq_Initialize(p);
    return (byte*)p;
}

void DestroyInstanceOf_MySeq(byte *pData) {
    free(pData);
}

void SetDataFor_MyChoice(void *dest, void *src)
{
    memcpy(dest, src, sizeof(MyChoice));
}

byte* MovePtrBySizeOf_MyChoice(byte *pData)
{
    return pData + sizeof(MyChoice);
}

byte* CreateInstanceOf_MyChoice() {
    MyChoice *p = (MyChoice*)malloc(sizeof(MyChoice));
    MyChoice_Initialize(p);
    return (byte*)p;
}

void DestroyInstanceOf_MyChoice(byte *pData) {
    free(pData);
}

void SetDataFor_MyEnum(void *dest, void *src)
{
    memcpy(dest, src, sizeof(MyEnum));
}

byte* MovePtrBySizeOf_MyEnum(byte *pData)
{
    return pData + sizeof(MyEnum);
}

byte* CreateInstanceOf_MyEnum() {
    MyEnum *p = (MyEnum*)malloc(sizeof(MyEnum));
    MyEnum_Initialize(p);
    return (byte*)p;
}

void DestroyInstanceOf_MyEnum(byte *pData) {
    free(pData);
}

void SetDataFor_MySeqOf(void *dest, void *src)
{
    memcpy(dest, src, sizeof(MySeqOf));
}

byte* MovePtrBySizeOf_MySeqOf(byte *pData)
{
    return pData + sizeof(MySeqOf);
}

byte* CreateInstanceOf_MySeqOf() {
    MySeqOf *p = (MySeqOf*)malloc(sizeof(MySeqOf));
    MySeqOf_Initialize(p);
    return (byte*)p;
}

void DestroyInstanceOf_MySeqOf(byte *pData) {
    free(pData);
}

void SetDataFor_int(void *dest, void *src)
{
    memcpy(dest, src, sizeof(int));
}

byte* MovePtrBySizeOf_int(byte *pData)
{
    return pData + sizeof(int);
}

byte* CreateInstanceOf_int() {
    int *p = (int*)malloc(sizeof(int));
    *p = 0;
    return (byte*)p;
}

void DestroyInstanceOf_int(byte *pData) {
    free(pData);
}

