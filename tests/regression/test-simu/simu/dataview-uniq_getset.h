#ifndef __GETSET_H__
#define __GETSET_H__

#include "dataview-uniq.h"

size_t GetStreamCurrentLength(BitStream *pBitStrm);
byte *GetBitstreamBuffer(BitStream *pBitStrm);
byte GetBufferByte(byte *p, size_t off);
void SetBufferByte(byte *p, size_t off, byte b);
void ResetStream(BitStream *pStrm);
BitStream *CreateStream(size_t bufferSize);
void DestroyStream(BitStream *pBitStrm);


/* INTEGER */
asn1SccSint T_UInt32__Get(T_UInt32* root);

/* INTEGER */
void T_UInt32__Set(T_UInt32* root, asn1SccSint value);

/* INTEGER */
asn1SccSint TASTE_Peek_id__Get(TASTE_Peek_id* root);

/* INTEGER */
void TASTE_Peek_id__Set(TASTE_Peek_id* root, asn1SccSint value);

/* SEQUENCEOF/SETOF */
long TASTE_Peek_id_list__GetLength(TASTE_Peek_id_list* root);

/* SEQUENCEOF/SETOF */
void TASTE_Peek_id_list__SetLength(TASTE_Peek_id_list* root, long value);

/* INTEGER */
asn1SccSint TASTE_Peek_id_list__iDx_Get(TASTE_Peek_id_list* root, int iDx);

/* INTEGER */
void TASTE_Peek_id_list__iDx_Set(TASTE_Peek_id_list* root, int iDx, asn1SccSint value);

/* SEQUENCEOF/SETOF */
long MySetOf__GetLength(MySetOf* root);

/* SEQUENCEOF/SETOF */
void MySetOf__SetLength(MySetOf* root, long value);

/* INTEGER */
asn1SccSint MySetOf__iDx_Get(MySetOf* root, int iDx);

/* INTEGER */
void MySetOf__iDx_Set(MySetOf* root, int iDx, asn1SccSint value);

/* INTEGER */
asn1SccSint MySimpleSeq__a_Get(MySimpleSeq* root);

/* INTEGER */
void MySimpleSeq__a_Set(MySimpleSeq* root, asn1SccSint value);

/* BOOLEAN */
flag MySimpleSeq__b_Get(MySimpleSeq* root);

/* BOOLEAN */
void MySimpleSeq__b_Set(MySimpleSeq* root, flag value);

/* ENUMERATED */
int MySimpleSeq__c_Get(MySimpleSeq* root);

/* ENUMERATED */
void MySimpleSeq__c_Set(MySimpleSeq* root, int value);

/* SEQUENCEOF/SETOF */
long FixedIntList__GetLength(FixedIntList* root);

/* SEQUENCEOF/SETOF */
void FixedIntList__SetLength(FixedIntList* root, long value);

/* INTEGER */
asn1SccSint FixedIntList__iDx_Get(FixedIntList* root, int iDx);

/* INTEGER */
void FixedIntList__iDx_Set(FixedIntList* root, int iDx, asn1SccSint value);

/* BOOLEAN */
flag MySeq__a_Get(MySeq* root);

/* BOOLEAN */
void MySeq__a_Set(MySeq* root, flag value);

/* Field b selector */
MyChoice* MySeq__b_Get(MySeq* root);

/* CHOICE selector */
int MySeq__b_kind_Get(MySeq* root);

/* CHOICE selector */
void MySeq__b_kind_Set(MySeq* root, int value);

/* BOOLEAN */
flag MySeq__b_a_Get(MySeq* root);

/* BOOLEAN */
void MySeq__b_a_Set(MySeq* root, flag value);

/* ENUMERATED */
int MySeq__b_b_Get(MySeq* root);

/* ENUMERATED */
void MySeq__b_b_Set(MySeq* root, int value);

/* CHOICE selector */
int MyChoice__kind_Get(MyChoice* root);

/* CHOICE selector */
void MyChoice__kind_Set(MyChoice* root, int value);

/* BOOLEAN */
flag MyChoice__a_Get(MyChoice* root);

/* BOOLEAN */
void MyChoice__a_Set(MyChoice* root, flag value);

/* ENUMERATED */
int MyChoice__b_Get(MyChoice* root);

/* ENUMERATED */
void MyChoice__b_Set(MyChoice* root, int value);

/* ENUMERATED */
int MyEnum__Get(MyEnum* root);

/* ENUMERATED */
void MyEnum__Set(MyEnum* root, int value);

/* SEQUENCEOF/SETOF */
long MySeqOf__GetLength(MySeqOf* root);

/* SEQUENCEOF/SETOF */
void MySeqOf__SetLength(MySeqOf* root, long value);

/* INTEGER */
asn1SccSint MySeqOf__iDx_Get(MySeqOf* root, int iDx);

/* INTEGER */
void MySeqOf__iDx_Set(MySeqOf* root, int iDx, asn1SccSint value);

/* Helper functions for NATIVE encodings */

void SetDataFor_T_UInt32(void *dest, void *src);
byte* MovePtrBySizeOf_T_UInt32(byte *pData);
byte* CreateInstanceOf_T_UInt32(void);
void DestroyInstanceOf_T_UInt32(byte *pData);

void SetDataFor_TASTE_Peek_id(void *dest, void *src);
byte* MovePtrBySizeOf_TASTE_Peek_id(byte *pData);
byte* CreateInstanceOf_TASTE_Peek_id(void);
void DestroyInstanceOf_TASTE_Peek_id(byte *pData);

void SetDataFor_TASTE_Peek_id_list(void *dest, void *src);
byte* MovePtrBySizeOf_TASTE_Peek_id_list(byte *pData);
byte* CreateInstanceOf_TASTE_Peek_id_list(void);
void DestroyInstanceOf_TASTE_Peek_id_list(byte *pData);

void SetDataFor_MySetOf(void *dest, void *src);
byte* MovePtrBySizeOf_MySetOf(byte *pData);
byte* CreateInstanceOf_MySetOf(void);
void DestroyInstanceOf_MySetOf(byte *pData);

void SetDataFor_MySimpleSeq(void *dest, void *src);
byte* MovePtrBySizeOf_MySimpleSeq(byte *pData);
byte* CreateInstanceOf_MySimpleSeq(void);
void DestroyInstanceOf_MySimpleSeq(byte *pData);

void SetDataFor_FixedIntList(void *dest, void *src);
byte* MovePtrBySizeOf_FixedIntList(byte *pData);
byte* CreateInstanceOf_FixedIntList(void);
void DestroyInstanceOf_FixedIntList(byte *pData);

void SetDataFor_MySeq(void *dest, void *src);
byte* MovePtrBySizeOf_MySeq(byte *pData);
byte* CreateInstanceOf_MySeq(void);
void DestroyInstanceOf_MySeq(byte *pData);

void SetDataFor_MyChoice(void *dest, void *src);
byte* MovePtrBySizeOf_MyChoice(byte *pData);
byte* CreateInstanceOf_MyChoice(void);
void DestroyInstanceOf_MyChoice(byte *pData);

void SetDataFor_MyEnum(void *dest, void *src);
byte* MovePtrBySizeOf_MyEnum(byte *pData);
byte* CreateInstanceOf_MyEnum(void);
void DestroyInstanceOf_MyEnum(byte *pData);

void SetDataFor_MySeqOf(void *dest, void *src);
byte* MovePtrBySizeOf_MySeqOf(byte *pData);
byte* CreateInstanceOf_MySeqOf(void);
void DestroyInstanceOf_MySeqOf(byte *pData);

void SetDataFor_int(void *dest, void *src);
byte* MovePtrBySizeOf_int(byte *pData);
byte* CreateInstanceOf_int(void);
void DestroyInstanceOf_int(byte *pData);


#endif
